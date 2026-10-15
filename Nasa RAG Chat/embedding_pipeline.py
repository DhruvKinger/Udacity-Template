#!/usr/bin/env python3
"""
ChromaDB Embedding Pipeline for NASA Space Mission Data - Text Files Only

This script reads parsed text data from various NASA space mission folders and creates
a permanent ChromaDB collection with OpenAI embeddings for RAG applications.
Optimized to process only text files to avoid duplication with JSON versions.

Supported data sources:
- Apollo 11 extracted data (text files only)
- Apollo 13 extracted data (text files only)
- Apollo 11 Textract extracted data (text files only)
- Challenger transcribed audio data (text files only)

Example usage:
    # Build / update the collection
    python embedding_pipeline.py --openai-key $OPENAI_API_KEY --data-path ./data_text

    # Re-process everything with different chunking, replacing old chunks
    python embedding_pipeline.py --openai-key $OPENAI_API_KEY --chunk-size 800 \\
        --chunk-overlap 150 --update-mode replace

    # Inspect the persisted collection (no API calls are made)
    python embedding_pipeline.py --stats-only
"""

import logging
import re
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

import chromadb
import openai
from chromadb.config import Settings

from openai_utils import DEFAULT_EMBEDDING_MODEL, get_api_key_from_env, get_openai_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chroma_embedding_text_only.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)  # one log line per API request is just noise

# Safety limit for a single embedding input (the API accepts ~8k tokens per input).
MAX_EMBEDDING_INPUT_CHARS = 24000

# Number of attempts for transient OpenAI errors (rate limits, timeouts, 5xx).
MAX_EMBEDDING_RETRIES = 5

# Separators that mark a natural place to end a chunk (checked from latest to earliest).
SENTENCE_BREAKS = ("\n\n", "\n", ". ", "? ", "! ", ".\n", "?\n", "!\n")


class FatalEmbeddingError(RuntimeError):
    """An error that retrying or moving to the next file cannot fix (bad API key, no access, unknown model)."""


class ChromaEmbeddingPipelineTextOnly:
    """Pipeline for creating ChromaDB collections with OpenAI embeddings - Text files only"""

    def __init__(self,
                 openai_api_key: str,
                 chroma_persist_directory: str = "./chroma_db",
                 collection_name: str = "nasa_space_missions_text",
                 embedding_model: str = DEFAULT_EMBEDDING_MODEL,
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        """
        Initialize the embedding pipeline

        Args:
            openai_api_key: OpenAI API key
            chroma_persist_directory: Directory to persist ChromaDB
            collection_name: Name of the ChromaDB collection
            embedding_model: OpenAI embedding model to use
            chunk_size: Maximum size of text chunks (in characters)
            chunk_overlap: Overlap between consecutive chunks (in characters)
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be >= 0 and smaller than chunk_size")
        if chunk_overlap > chunk_size // 2:
            logger.warning(
                f"chunk_overlap ({chunk_overlap}) is more than half of chunk_size ({chunk_size}): "
                f"this creates many near-duplicate chunks and a larger embedding bill."
            )

        # Initialize OpenAI client
        self.openai_client = get_openai_client(openai_api_key)

        # Store configuration parameters
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.collection_name = collection_name
        self.chroma_persist_directory = chroma_persist_directory

        # Initialize ChromaDB client (persistent, on disk)
        Path(chroma_persist_directory).mkdir(parents=True, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        # Create or get the collection. Embeddings are computed by this pipeline (and by the
        # RAG client at query time) with the same OpenAI model, so no Chroma embedding
        # function is attached. The model name is stored in the collection metadata so the
        # retrieval side always embeds questions with the model used to index the chunks.
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=None,
            metadata={
                "description": "NASA space mission documents (Apollo 11, Apollo 13, Challenger)",
                "embedding_model": embedding_model,
            },
            configuration={"hnsw": {"space": "cosine"}},
        )

        existing_model = (self.collection.metadata or {}).get("embedding_model")
        if existing_model and existing_model != embedding_model:
            logger.warning(
                f"Collection '{collection_name}' was built with embedding model "
                f"'{existing_model}' but '{embedding_model}' was requested. Mixing models in one "
                f"collection gives meaningless search results - use --update-mode replace "
                f"or a different --collection-name."
            )
        logger.info(
            f"Collection '{collection_name}' ready at '{chroma_persist_directory}' "
            f"({self.collection.count()} chunks, chunk_size={chunk_size}, "
            f"chunk_overlap={chunk_overlap}, model={embedding_model})"
        )

    # ------------------------------------------------------------------
    # Chunking
    # ------------------------------------------------------------------
    def _find_chunk_end(self, text: str, start: int, hard_end: int) -> int:
        """
        Choose where a chunk that starts at ``start`` should end.

        The chunk may never extend past ``hard_end`` (start + chunk_size). We prefer to end
        on a sentence/line boundary, but never earlier than ``min_end`` so that every chunk
        is long enough to move the window forward by more than ``chunk_overlap`` characters.
        """
        min_end = start + max(self.chunk_size // 2, self.chunk_overlap + 1)
        min_end = min(min_end, hard_end)

        best = -1
        for sep in SENTENCE_BREAKS:
            idx = text.rfind(sep, max(start, min_end - len(sep)), hard_end)
            if idx != -1:
                best = max(best, idx + len(sep))
        if best >= min_end:
            return best

        # No sentence boundary available: avoid cutting a word in half if we can.
        idx = text.rfind(" ", min_end, hard_end)
        if idx != -1:
            return idx + 1

        return hard_end

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Split text into chunks with metadata

        Guarantees:
        - no chunk is longer than ``self.chunk_size`` characters
        - consecutive chunks overlap by exactly ``self.chunk_overlap`` characters
          (the last ``chunk_overlap`` characters of chunk *i* are the first ones of chunk *i+1*)
        - chunks end on a sentence / line boundary whenever one is available

        Args:
            text: Text to chunk
            metadata: Base metadata for the text

        Returns:
            List of (chunk_text, chunk_metadata) tuples
        """
        if not text or not text.strip():
            return []

        # Short texts don't need chunking
        if len(text) <= self.chunk_size:
            chunk_metadata = dict(metadata)
            chunk_metadata.update({
                'chunk_index': 0,
                'total_chunks': 1,
                'chunk_start': 0,
                'chunk_end': len(text),
                'chunk_length': len(text),
            })
            return [(text, chunk_metadata)]

        spans: List[Tuple[int, int]] = []
        n = len(text)
        start = 0
        while start < n:
            hard_end = min(start + self.chunk_size, n)
            end = n if hard_end >= n else self._find_chunk_end(text, start, hard_end)

            if text[start:end].strip():
                spans.append((start, end))

            if end >= n:
                break
            # Do not emit a trailing chunk that would only repeat the overlap + whitespace
            if not text[end:].strip():
                break
            start = end - self.chunk_overlap

        total = len(spans)
        chunks: List[Tuple[str, Dict[str, Any]]] = []
        for index, (chunk_start, chunk_end) in enumerate(spans):
            chunk_metadata = dict(metadata)
            chunk_metadata.update({
                'chunk_index': index,
                'total_chunks': total,
                'chunk_start': chunk_start,
                'chunk_end': chunk_end,
                'chunk_length': chunk_end - chunk_start,
            })
            chunks.append((text[chunk_start:chunk_end], chunk_metadata))
        return chunks

    # ------------------------------------------------------------------
    # Document management
    # ------------------------------------------------------------------
    def check_document_exists(self, doc_id: str) -> bool:
        """
        Check if a document with the given ID already exists in the collection

        Args:
            doc_id: Document ID to check

        Returns:
            True if document exists, False otherwise
        """
        try:
            result = self.collection.get(ids=[doc_id], include=[])
            return len(result.get('ids', [])) > 0
        except Exception as e:
            logger.error(f"Error checking document {doc_id}: {e}")
            return False

    def _existing_ids(self, doc_ids: List[str]) -> Set[str]:
        """Return the subset of ``doc_ids`` that already exist (one query for many ids)."""
        if not doc_ids:
            return set()
        result = self.collection.get(ids=doc_ids, include=[])
        return set(result.get('ids', []))

    def update_document(self, doc_id: str, text: str, metadata: Dict[str, Any]) -> bool:
        """
        Update an existing document in the collection

        Args:
            doc_id: Document ID to update
            text: New text content
            metadata: New metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get new embedding
            embedding = self.get_embedding(text)

            # Update the document
            self.collection.update(
                ids=[doc_id],
                documents=[text],
                metadatas=[metadata],
                embeddings=[embedding]
            )
            logger.debug(f"Updated document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating document {doc_id}: {e}")
            return False

    def delete_documents_by_source(self, source_pattern: str) -> int:
        """
        Delete all documents from a specific source (useful for re-processing files)

        Args:
            source_pattern: Pattern to match source names

        Returns:
            Number of documents deleted
        """
        try:
            # Get all documents (metadata only - the text is not needed here)
            all_docs = self.collection.get(include=['metadatas'])

            # Find documents matching the source pattern
            ids_to_delete = []
            for i, metadata in enumerate(all_docs['metadatas']):
                if source_pattern in metadata.get('source', ''):
                    ids_to_delete.append(all_docs['ids'][i])

            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} documents matching source pattern: {source_pattern}")
                return len(ids_to_delete)
            else:
                logger.info(f"No documents found matching source pattern: {source_pattern}")
                return 0

        except Exception as e:
            logger.error(f"Error deleting documents by source: {e}")
            return 0

    def get_file_documents(self, file_path: Path) -> List[str]:
        """
        Get all document IDs for a specific file

        Args:
            file_path: Path to the file

        Returns:
            List of document IDs for the file
        """
        try:
            source = file_path.stem
            mission = self.extract_mission_from_path(file_path)

            # Ask Chroma for exactly the chunks of this file (ids only)
            result = self.collection.get(
                where={"$and": [{"source": source}, {"mission": mission}]},
                include=[]
            )
            return list(result.get('ids', []))

        except Exception as e:
            logger.error(f"Error getting file documents: {e}")
            return []

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Get OpenAI embeddings for several texts with a single API request.

        Transient errors (rate limits, timeouts, server errors) are retried with
        exponential back-off.

        Args:
            texts: Texts to embed

        Returns:
            Embedding vectors, in the same order as ``texts``
        """
        if not texts:
            return []

        # The API rejects empty strings and very long inputs
        inputs = [(t[:MAX_EMBEDDING_INPUT_CHARS] if t.strip() else " ") for t in texts]

        transient_errors = (openai.RateLimitError, openai.APIConnectionError,
                            openai.APITimeoutError, openai.InternalServerError)
        last_error: Optional[Exception] = None
        for attempt in range(MAX_EMBEDDING_RETRIES):
            try:
                response = self.openai_client.embeddings.create(
                    model=self.embedding_model,
                    input=inputs
                )
                ordered = sorted(response.data, key=lambda item: item.index)
                embeddings = [item.embedding for item in ordered]
                if len(embeddings) != len(inputs):
                    raise RuntimeError(
                        f"Expected {len(inputs)} embeddings but received {len(embeddings)}"
                    )
                return embeddings
            except transient_errors as e:
                last_error = e
                wait = min(2 ** attempt, 30)
                logger.warning(f"Transient OpenAI error ({type(e).__name__}); "
                               f"retrying in {wait}s (attempt {attempt + 1}/{MAX_EMBEDDING_RETRIES})")
                time.sleep(wait)
            except (openai.AuthenticationError, openai.PermissionDeniedError, openai.NotFoundError) as e:
                raise FatalEmbeddingError(
                    f"OpenAI rejected the request ({type(e).__name__}). Check that your API key is valid "
                    f"(OpenAI keys start with 'sk-', Udacity keys with 'voc-') and that it can use the "
                    f"embedding model '{self.embedding_model}'. Details: {e}"
                ) from e
            except Exception as e:
                raise RuntimeError(f"Embedding request failed: {e}") from e

        raise RuntimeError(
            f"Embedding request failed after {MAX_EMBEDDING_RETRIES} attempts: {last_error}"
        ) from last_error

    def get_embedding(self, text: str) -> List[float]:
        """
        Get OpenAI embedding for text

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        if text is None:
            raise ValueError("Cannot create an embedding for None")
        try:
            return self.get_embeddings_batch([text])[0]
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise

    def generate_document_id(self, file_path: Path, metadata: Dict[str, Any]) -> str:
        """
        Generate stable document ID based on file path and chunk position
        This allows for document updates without changing IDs

        Format: mission_source_chunk_0001
        """
        mission = metadata.get('mission') or self.extract_mission_from_path(file_path)
        source = metadata.get('source') or file_path.stem
        chunk_index = int(metadata.get('chunk_index', 0))

        safe_source = re.sub(r'[^A-Za-z0-9_.-]+', '_', str(source))
        return f"{mission}_{safe_source}_chunk_{chunk_index:04d}"

    # ------------------------------------------------------------------
    # File processing
    # ------------------------------------------------------------------
    def process_text_file(self, file_path: Path) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Process plain text files with enhanced metadata extraction

        Args:
            file_path: Path to text file

        Returns:
            List of (text, metadata) tuples
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                return []

            # Enhanced metadata extraction
            metadata = {
                'source': file_path.stem,
                'file_path': str(file_path),
                'file_type': 'text',
                'content_type': 'full_text',
                'mission': self.extract_mission_from_path(file_path),
                'data_type': self.extract_data_type_from_path(file_path),
                'document_category': self.extract_document_category_from_filename(file_path.name),
                'file_size': len(content),
                'processed_timestamp': datetime.now().isoformat()
            }

            return self.chunk_text(content, metadata)

        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            return []

    def extract_mission_from_path(self, file_path: Path) -> str:
        """Extract mission name from file path"""
        path_str = str(file_path).lower()
        if 'apollo11' in path_str or 'apollo_11' in path_str:
            return 'apollo_11'
        elif 'apollo13' in path_str or 'apollo_13' in path_str:
            return 'apollo_13'
        elif 'challenger' in path_str:
            return 'challenger'
        else:
            return 'unknown'

    def extract_data_type_from_path(self, file_path: Path) -> str:
        """Extract data type from file path"""
        path_str = str(file_path).lower()
        if 'transcript' in path_str:
            return 'transcript'
        elif 'textract' in path_str:
            return 'textract_extracted'
        elif 'audio' in path_str:
            return 'audio_transcript'
        elif 'flight_plan' in path_str:
            return 'flight_plan'
        else:
            return 'document'

    def extract_document_category_from_filename(self, filename: str) -> str:
        """Extract document category from filename for better organization"""
        filename_lower = filename.lower()

        # Apollo transcript types
        if 'pao' in filename_lower:
            return 'public_affairs_officer'
        elif 'cm' in filename_lower:
            return 'command_module'
        elif 'tec' in filename_lower:
            return 'technical'
        elif 'flight_plan' in filename_lower:
            return 'flight_plan'

        # Challenger audio segments
        elif 'mission_audio' in filename_lower:
            return 'mission_audio'

        # NASA archive documents
        elif 'ntrs' in filename_lower:
            return 'nasa_archive'
        elif '19900066485' in filename_lower:
            return 'technical_report'
        elif '19710015566' in filename_lower:
            return 'mission_report'

        # General categories
        elif 'full_text' in filename_lower:
            return 'complete_document'
        else:
            return 'general_document'

    def scan_text_files_only(self, base_path: str) -> List[Path]:
        """
        Scan data directories for text files only (avoiding JSON duplicates)

        Args:
            base_path: Base directory path

        Returns:
            List of text file paths to process
        """
        base_path = Path(base_path)
        files_to_process = []

        # Define directories to scan
        data_dirs = [
            'apollo11',
            'apollo13',
            'challenger'
        ]

        for data_dir in data_dirs:
            dir_path = base_path / data_dir
            if dir_path.exists():
                logger.info(f"Scanning directory: {dir_path}")

                # Find only text files
                text_files = sorted(dir_path.glob('**/*.txt'))
                files_to_process.extend(text_files)
                logger.info(f"Found {len(text_files)} text files in {data_dir}")

        # Filter out unwanted files
        filtered_files = []
        for file_path in files_to_process:
            # Skip system files and summaries
            if (file_path.name.startswith('.') or
                'summary' in file_path.name.lower() or
                file_path.suffix.lower() != '.txt'):
                continue
            filtered_files.append(file_path)

        logger.info(f"Total text files to process: {len(filtered_files)}")

        # Log file breakdown by mission
        mission_counts = {}
        for file_path in filtered_files:
            mission = self.extract_mission_from_path(file_path)
            mission_counts[mission] = mission_counts.get(mission, 0) + 1

        logger.info("Files by mission:")
        for mission, count in mission_counts.items():
            logger.info(f"  {mission}: {count} files")

        return filtered_files

    def add_documents_to_collection(self, documents: List[Tuple[str, Dict[str, Any]]],
                                   file_path: Path, batch_size: int = 50,
                                   update_mode: str = 'skip') -> Dict[str, int]:
        """
        Add documents to ChromaDB collection in batches with update handling

        Args:
            documents: List of (text, metadata) tuples
            file_path: Path to the source file
            batch_size: Number of documents to process in each batch
            update_mode: How to handle existing documents:
                        'skip' - skip existing documents
                        'update' - update existing documents
                        'replace' - delete all existing documents from file and re-add

        Returns:
            Dictionary with counts of added, updated, and skipped documents
        """
        if not documents:
            return {'added': 0, 'updated': 0, 'skipped': 0}

        if update_mode not in ('skip', 'update', 'replace'):
            raise ValueError(f"Invalid update_mode '{update_mode}' (use skip, update or replace)")
        if batch_size <= 0:
            raise ValueError("batch_size must be a positive integer")

        stats = {'added': 0, 'updated': 0, 'skipped': 0}

        # Handle the update modes that need work before the batches are processed
        if update_mode == 'replace':
            # Remove every chunk previously stored for this file, then add everything fresh
            old_ids = self.get_file_documents(file_path)
            if old_ids:
                self.collection.delete(ids=old_ids)
                logger.info(f"Replace mode: removed {len(old_ids)} existing chunks of {file_path.name}")

        # Process documents in batches
        for batch_start in range(0, len(documents), batch_size):
            batch = documents[batch_start:batch_start + batch_size]
            batch_ids = [self.generate_document_id(file_path, metadata) for _, metadata in batch]

            # One lookup tells us which chunks are already stored
            existing_ids = set() if update_mode == 'replace' else self._existing_ids(batch_ids)

            new_items = []       # (id, text, metadata)
            changed_items = []   # (id, text, metadata)
            for doc_id, (text, metadata) in zip(batch_ids, batch):
                if doc_id in existing_ids:
                    if update_mode == 'skip':
                        stats['skipped'] += 1
                        continue
                    changed_items.append((doc_id, text, metadata))
                else:
                    new_items.append((doc_id, text, metadata))

            to_embed = new_items + changed_items
            if not to_embed:
                continue

            # Get the embeddings for the whole batch with one API request
            embeddings = self.get_embeddings_batch([text for _, text, _ in to_embed])
            new_embeddings = embeddings[:len(new_items)]
            changed_embeddings = embeddings[len(new_items):]

            if new_items:
                self.collection.add(
                    ids=[doc_id for doc_id, _, _ in new_items],
                    documents=[text for _, text, _ in new_items],
                    metadatas=[metadata for _, _, metadata in new_items],
                    embeddings=new_embeddings
                )
                stats['added'] += len(new_items)

            if changed_items:
                self.collection.update(
                    ids=[doc_id for doc_id, _, _ in changed_items],
                    documents=[text for _, text, _ in changed_items],
                    metadatas=[metadata for _, _, metadata in changed_items],
                    embeddings=changed_embeddings
                )
                stats['updated'] += len(changed_items)

        # In update mode a re-chunked file may now have fewer chunks: drop the stale ones
        if update_mode == 'update':
            current_ids = {self.generate_document_id(file_path, metadata) for _, metadata in documents}
            stale_ids = [doc_id for doc_id in self.get_file_documents(file_path)
                         if doc_id not in current_ids]
            if stale_ids:
                self.collection.delete(ids=stale_ids)
                logger.info(f"Update mode: removed {len(stale_ids)} stale chunks of {file_path.name}")

        return stats

    def process_all_text_data(self, base_path: str, update_mode: str = 'skip',
                              batch_size: int = 50) -> Dict[str, int]:
        """
        Process all text files and add to ChromaDB

        Args:
            base_path: Base directory containing data folders
            update_mode: How to handle existing documents:
                        'skip' - skip existing documents (default)
                        'update' - update existing documents
                        'replace' - delete all existing documents from file and re-add
            batch_size: Number of chunks embedded per OpenAI request

        Returns:
            Statistics about processed files
        """
        stats = {
            'files_processed': 0,
            'documents_added': 0,
            'documents_updated': 0,
            'documents_skipped': 0,
            'errors': 0,
            'total_chunks': 0,
            'missions': {}
        }

        # Get files to process
        files_to_process = self.scan_text_files_only(base_path)
        if not files_to_process:
            logger.warning(f"No text files found under '{base_path}'. "
                           f"Expected sub-folders apollo11/, apollo13/ and challenger/.")
            return stats

        # Loop through each file
        for position, file_path in enumerate(files_to_process, start=1):
            mission = self.extract_mission_from_path(file_path)
            mission_stats = stats['missions'].setdefault(
                mission, {'files': 0, 'chunks': 0, 'added': 0, 'updated': 0, 'skipped': 0}
            )

            try:
                logger.info(f"[{position}/{len(files_to_process)}] Processing {file_path.name} ({mission})")

                # Process file and add to collection
                documents = self.process_text_file(file_path)
                if not documents:
                    logger.warning(f"No content extracted from {file_path.name}")
                    continue

                file_stats = self.add_documents_to_collection(
                    documents, file_path, batch_size=batch_size, update_mode=update_mode
                )

                # Update statistics
                stats['files_processed'] += 1
                stats['total_chunks'] += len(documents)
                stats['documents_added'] += file_stats['added']
                stats['documents_updated'] += file_stats['updated']
                stats['documents_skipped'] += file_stats['skipped']

                mission_stats['files'] += 1
                mission_stats['chunks'] += len(documents)
                mission_stats['added'] += file_stats['added']
                mission_stats['updated'] += file_stats['updated']
                mission_stats['skipped'] += file_stats['skipped']

                logger.info(f"  {len(documents)} chunks -> added {file_stats['added']}, "
                            f"updated {file_stats['updated']}, skipped {file_stats['skipped']}")

            except FatalEmbeddingError:
                raise  # no point trying the remaining files: stop and report it
            except Exception as e:
                # Handle errors gracefully: log, count and continue with the next file.
                # Re-running with the default 'skip' mode resumes where this stopped.
                stats['errors'] += 1
                logger.error(f"Failed to process {file_path.name}: {e}")

        return stats

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the ChromaDB collection"""
        try:
            return {
                'collection_name': self.collection_name,
                'document_count': self.collection.count(),
                'metadata': self.collection.metadata,
                'embedding_model': self.embedding_model,
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap,
                'persist_directory': self.chroma_persist_directory,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {'collection_name': self.collection_name, 'error': str(e)}

    def query_collection(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Query the collection for testing

        Args:
            query_text: Query text
            n_results: Number of results to return

        Returns:
            Query results
        """
        try:
            query_embedding = self.get_embedding(query_text)
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
        except Exception as e:
            logger.error(f"Error querying collection: {e}")
            return {}

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get detailed statistics about the collection"""
        try:
            # Get all documents to analyze (metadata only)
            all_docs = self.collection.get(include=['metadatas'])

            stats = {
                'total_documents': len(all_docs['metadatas']),
                'missions': {},
                'data_types': {},
                'document_categories': {},
                'file_types': {},
                'sources': {}
            }

            # Analyze metadata
            for metadata in all_docs['metadatas']:
                mission = metadata.get('mission', 'unknown')
                data_type = metadata.get('data_type', 'unknown')
                doc_category = metadata.get('document_category', 'unknown')
                file_type = metadata.get('file_type', 'unknown')
                source = metadata.get('source', 'unknown')

                # Count by mission
                stats['missions'][mission] = stats['missions'].get(mission, 0) + 1

                # Count by data type
                stats['data_types'][data_type] = stats['data_types'].get(data_type, 0) + 1

                # Count by document category
                stats['document_categories'][doc_category] = stats['document_categories'].get(doc_category, 0) + 1

                # Count by file type
                stats['file_types'][file_type] = stats['file_types'].get(file_type, 0) + 1

                # Count by source file
                stats['sources'][source] = stats['sources'].get(source, 0) + 1

            return stats

        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'error': str(e)}


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='ChromaDB Embedding Pipeline for NASA Data')
    parser.add_argument('--data-path', default='./data_text', help='Path to data directories')
    parser.add_argument('--openai-key', default=None,
                        help='OpenAI API key (defaults to the OPENAI_API_KEY environment variable)')
    parser.add_argument('--chroma-dir', default='./chroma_db_openai', help='ChromaDB persist directory')
    parser.add_argument('--collection-name', default='nasa_space_missions_text', help='Collection name')
    parser.add_argument('--embedding-model', default=DEFAULT_EMBEDDING_MODEL, help='OpenAI embedding model')
    parser.add_argument('--chunk-size', type=int, default=500, help='Maximum chunk size in characters')
    parser.add_argument('--chunk-overlap', type=int, default=100, help='Overlap between chunks in characters')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for processing')
    parser.add_argument('--update-mode', choices=['skip', 'update', 'replace'], default='skip',
                       help='How to handle existing documents: skip, update, or replace')
    parser.add_argument('--test-query', help='Test query after processing')
    parser.add_argument('--stats-only', action='store_true', help='Only show collection statistics')
    parser.add_argument('--delete-source', help='Delete all documents from a specific source pattern')

    args = parser.parse_args()

    # An API key is only needed when embeddings have to be created
    api_key = args.openai_key or get_api_key_from_env()
    needs_api = not (args.stats_only or args.delete_source)
    if needs_api and not api_key:
        parser.error("an OpenAI API key is required: pass --openai-key or set OPENAI_API_KEY")
    api_key = api_key or "not-needed-for-this-command"

    # Initialize pipeline
    logger.info("Initializing ChromaDB Embedding Pipeline...")
    try:
        pipeline = ChromaEmbeddingPipelineTextOnly(
            openai_api_key=api_key,
            chroma_persist_directory=args.chroma_dir,
            collection_name=args.collection_name,
            embedding_model=args.embedding_model,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )
    except ValueError as e:
        parser.error(str(e))

    # Handle delete source operation
    if args.delete_source:
        deleted_count = pipeline.delete_documents_by_source(args.delete_source)
        logger.info(f"Deleted {deleted_count} documents matching source pattern: {args.delete_source}")
        return

    # If stats only, show collection statistics and exit
    if args.stats_only:
        collection_info = pipeline.get_collection_info()
        logger.info("Collection Statistics:")
        logger.info(f"collection_name: {collection_info.get('collection_name', 'N/A')}")
        logger.info(f"persist_directory: {args.chroma_dir}")
        logger.info(f"collection_size (chunks): {collection_info.get('document_count', 'N/A')}")
        stats = pipeline.get_collection_stats()
        if stats.get('total_documents', 0) == 0 and 'error' not in stats:
            logger.info("The collection is empty - run the pipeline first (without --stats-only).")
        for key, value in stats.items():
            logger.info(f"{key}: {value}")
        return

    # Process all data
    logger.info(f"Starting text data processing with update mode: {args.update_mode}")
    start_time = time.time()

    try:
        stats = pipeline.process_all_text_data(
            args.data_path, update_mode=args.update_mode, batch_size=args.batch_size
        )
    except FatalEmbeddingError as e:
        logger.error(f"Stopping: {e}")
        logger.error("Nothing more was processed. Fix the problem above and run the same command again "
                     "(already stored chunks are skipped).")
        sys.exit(1)

    end_time = time.time()
    processing_time = end_time - start_time

    # Print results
    logger.info("=" * 60)
    logger.info("PROCESSING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Files processed: {stats['files_processed']}")
    logger.info(f"Total chunks created: {stats['total_chunks']}")
    logger.info(f"Documents added to collection: {stats['documents_added']}")
    logger.info(f"Documents updated in collection: {stats['documents_updated']}")
    logger.info(f"Documents skipped (already exist): {stats['documents_skipped']}")
    logger.info(f"Errors: {stats['errors']}")
    logger.info(f"Processing time: {processing_time:.2f} seconds")

    # Mission breakdown
    logger.info("\nMission breakdown:")
    for mission, mission_stats in stats['missions'].items():
        logger.info(f"  {mission}: {mission_stats['files']} files, {mission_stats['chunks']} chunks")
        logger.info(f"    Added: {mission_stats['added']}, Updated: {mission_stats['updated']}, Skipped: {mission_stats['skipped']}")

    # Collection info
    collection_info = pipeline.get_collection_info()
    logger.info(f"\nCollection: {collection_info.get('collection_name', 'N/A')}")
    logger.info(f"Total documents in collection: {collection_info.get('document_count', 'N/A')}")

    # Test query if provided
    if args.test_query:
        logger.info(f"\nTesting query: '{args.test_query}'")
        results = pipeline.query_collection(args.test_query)
        if results and 'documents' in results:
            logger.info(f"Found {len(results['documents'][0])} results:")
            for i, doc in enumerate(results['documents'][0][:3]):  # Show top 3
                logger.info(f"Result {i+1}: {doc[:200]}...")

    if stats['errors']:
        logger.error(f"Pipeline finished with {stats['errors']} failed file(s) - see the errors above. "
                     f"Re-run the same command to retry only what is missing.")
        sys.exit(1)
    logger.info("Pipeline completed successfully!")


if __name__ == "__main__":
    main()
