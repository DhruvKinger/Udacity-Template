"""RAG client: ChromaDB discovery, semantic retrieval and context formatting.

The retrieval flow is:

1. ``discover_chroma_backends``  - find persisted ChromaDB collections next to the app
2. ``initialize_rag_system``     - open one collection
3. ``retrieve_documents``        - embed the question with OpenAI and run a similarity query
                                   (top-k, optional mission metadata filter, de-duplicated)
4. ``format_context``            - turn the retrieved chunks into one clean context string
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import chromadb
from chromadb.config import Settings

from openai_utils import DEFAULT_EMBEDDING_MODEL, get_api_key_from_env, get_openai_client

logger = logging.getLogger(__name__)

# Chunks longer than this are shortened when they are put into the LLM context.
MAX_CONTEXT_CHARS_PER_DOCUMENT = 1500

# Values of the mission filter that mean "do not filter".
_NO_FILTER_VALUES = {"", "all", "all missions", "any", "none"}

# We fetch more candidates than requested so that de-duplication can still return k results.
_OVERFETCH_FACTOR = 3


# Words that identify a mission in a question (used by "auto-detect"). Only unambiguous
# names are listed: crew names and the explicit mission names.
_MISSION_PATTERNS = {
    "apollo_11": r"apollo[\s_-]*11\b|\ba11\b|armstrong|aldrin|michael collins|tranquility",
    "apollo_13": r"apollo[\s_-]*13\b|\ba13\b|lovell|swigert|haise",
    "challenger": r"challenger|sts[\s_-]*51[\s_-]*l|\b51[\s_-]*l\b|mcauliffe|scobee|scobie|resnik|resnick|onizuka|mcnair|jarvis",
}


def detect_mission(question: str) -> Optional[str]:
    """Guess which mission a question is about from words in the question itself.

    Returns ``"apollo_11"``, ``"apollo_13"`` or ``"challenger"`` when exactly one mission is
    mentioned, otherwise ``None`` (no mission mentioned, or several -> search all missions).
    """
    text = (question or "").lower()
    found = [mission for mission, pattern in _MISSION_PATTERNS.items() if re.search(pattern, text)]
    return found[0] if len(found) == 1 else None


def _get_chroma_client(chroma_dir: str):
    """Open a persistent ChromaDB client (same settings everywhere so clients can be shared)."""
    return chromadb.PersistentClient(
        path=str(chroma_dir),
        settings=Settings(anonymized_telemetry=False)
    )


def discover_chroma_backends() -> Dict[str, Dict[str, str]]:
    """Discover available ChromaDB backends in the project directory"""
    backends = {}
    current_dir = Path(".")

    # Look for ChromaDB directories: real directories whose name contains "chroma" and that
    # hold a Chroma database file (this avoids creating a database in unrelated folders).
    chroma_dirs = sorted(
        path for path in current_dir.iterdir()
        if path.is_dir()
        and "chroma" in path.name.lower()
        and not path.name.startswith(".")
        and (path / "chroma.sqlite3").exists()
    )

    # Loop through each discovered directory
    for chroma_dir in chroma_dirs:
        # Wrap connection attempt in try-except block for error handling
        try:
            # Initialize database client with directory path and configuration settings
            client = _get_chroma_client(str(chroma_dir))

            # Retrieve list of available collections from the database
            collections = client.list_collections()

            # Loop through each collection found
            for collection in collections:
                # (older Chroma versions return names, newer ones return Collection objects)
                collection_name = collection if isinstance(collection, str) else collection.name

                # Create unique identifier key combining directory and collection names
                key = f"{chroma_dir.name}/{collection_name}"

                # Get document count with fallback for unsupported operations
                try:
                    count = client.get_collection(collection_name).count()
                except Exception:
                    count = "unknown"

                # Build information dictionary and add it to the backends dictionary
                backends[key] = {
                    "directory": str(chroma_dir),
                    "collection_name": collection_name,
                    "display_name": f"{collection_name} ({count} docs) - {chroma_dir.name}",
                    "count": str(count),
                }

        except Exception as e:
            # Handle connection or access errors gracefully with a fallback entry
            error_text = str(e)
            if len(error_text) > 60:
                error_text = error_text[:60] + "..."
            backends[f"{chroma_dir.name}/error"] = {
                "directory": str(chroma_dir),
                "collection_name": "",
                "display_name": f"{chroma_dir.name} (error: {error_text})",
                "count": "0",
            }

    # Return complete backends dictionary with all discovered collections
    return backends


def initialize_rag_system(chroma_dir: str, collection_name: str) -> Tuple[Optional[object], bool, Optional[str]]:
    """Initialize the RAG system with specified backend (cached for performance)

    Returns:
        ``(collection, success, error_message)`` - the format expected by ``chat.py``.
        On failure ``collection`` is ``None`` and ``error_message`` explains what went wrong.
    """
    try:
        # Create a chromadb persistent client
        client = _get_chroma_client(chroma_dir)

        # Return the collection with the collection_name
        collection = client.get_collection(name=collection_name)
        return collection, True, None
    except Exception as e:
        logger.error(f"Could not open collection '{collection_name}' in '{chroma_dir}': {e}")
        return None, False, str(e)


def _normalize_mission_filter(mission_filter: Optional[str]) -> Optional[str]:
    """Convert a user-facing mission name ("Apollo 11") to the stored metadata value ("apollo_11").

    Returns ``None`` when no filtering was requested.
    """
    if mission_filter is None:
        return None
    text = str(mission_filter).strip().lower()
    if text in _NO_FILTER_VALUES:
        return None
    return text.replace("-", "_").replace(" ", "_")


def _embed_query(collection, query: str, api_key: Optional[str]) -> List[float]:
    """Embed the question with the same OpenAI model that was used to index the collection."""
    key = api_key or get_api_key_from_env()
    if not key:
        raise ValueError(
            "An OpenAI API key is required to embed the question "
            "(pass api_key or set OPENAI_API_KEY)."
        )
    model = (collection.metadata or {}).get("embedding_model", DEFAULT_EMBEDDING_MODEL)
    client = get_openai_client(key)
    response = client.embeddings.create(model=model, input=[query])
    return response.data[0].embedding


def _deduplicate_and_rank(results: Dict, n_results: int) -> Dict:
    """Sort retrieved chunks by similarity and drop repeated / contained snippets."""
    ids = (results.get("ids") or [[]])[0]
    documents = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]

    rows = []
    for position, document in enumerate(documents):
        rows.append({
            "id": ids[position] if position < len(ids) else None,
            "document": document,
            "metadata": dict(metadatas[position] or {}) if position < len(metadatas) else {},
            "distance": distances[position] if position < len(distances) else None,
        })

    # Most similar (smallest distance) first
    rows.sort(key=lambda row: row["distance"] if row["distance"] is not None else float("inf"))

    kept, seen_texts = [], []
    for row in rows:
        normalized = " ".join((row["document"] or "").lower().split())
        if not normalized:
            continue
        # skip exact repeats and snippets fully contained in a better-ranked snippet
        if any(normalized == other or normalized in other for other in seen_texts):
            continue
        seen_texts.append(normalized)
        if row["distance"] is not None:
            row["metadata"]["distance"] = round(float(row["distance"]), 4)
        kept.append(row)
        if len(kept) >= n_results:
            break

    return {
        "ids": [[row["id"] for row in kept]],
        "documents": [[row["document"] for row in kept]],
        "metadatas": [[row["metadata"] for row in kept]],
        "distances": [[row["distance"] for row in kept]],
    }


def retrieve_documents(collection, query: str, n_results: int = 3,
                      mission_filter: Optional[str] = None,
                      api_key: Optional[str] = None,
                      query_expansion: Optional[str] = None) -> Optional[Dict]:
    """Retrieve relevant documents from ChromaDB with optional filtering

    Args:
        collection: ChromaDB collection returned by ``initialize_rag_system``
        query: The user's question
        n_results: Number of chunks to return (top-k)
        mission_filter: ``None`` / "all" for no filtering, otherwise a mission such as
                        "apollo_11", "apollo_13" or "challenger" ("Apollo 11" also works)
        api_key: OpenAI key used to embed the question (defaults to the environment)
        query_expansion: Optional archive-style rewrite of the question (see
                        ``llm_client.expand_query``). It is embedded together with the question.

    Returns:
        Chroma-style result dict (``ids``, ``documents``, ``metadatas``, ``distances``; each a
        list holding one list), sorted by similarity and de-duplicated.
    """
    if collection is None:
        raise ValueError("No ChromaDB collection is available.")
    if not query or not query.strip():
        raise ValueError("The question must not be empty.")
    n_results = max(1, int(n_results))

    # Initialize filter variable to None (represents no filtering)
    where_filter = None

    # Only filter when a specific mission was requested
    mission = _normalize_mission_filter(mission_filter)
    if mission:
        where_filter = {"mission": mission}

    total = collection.count()
    if total == 0:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    # Execute the similarity query using the embedding of the question
    search_text = query.strip()
    if query_expansion and query_expansion.strip():
        search_text = f"{search_text}\n{query_expansion.strip()}"
    query_embedding = _embed_query(collection, search_text, api_key)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results * _OVERFETCH_FACTOR, total),
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    # Return query results to caller (ranked by similarity, repeated snippets removed)
    return _deduplicate_and_rank(results, n_results)


def format_context(documents: List[str], metadatas: List[Dict]) -> str:
    """Format retrieved documents into context"""
    if not documents:
        return ""

    metadatas = metadatas or []

    # Header text for the context section
    context_parts = ["Retrieved context from NASA mission archives (most relevant first):"]

    # Loop through paired documents and their metadata using enumeration
    for i, document in enumerate(documents, start=1):
        metadata = (metadatas[i - 1] if i - 1 < len(metadatas) else None) or {}

        # Mission and category: replace underscores and capitalize for display
        mission = str(metadata.get("mission", "unknown")).replace("_", " ").title()
        source = metadata.get("source", "unknown")
        category = str(metadata.get("document_category", "unknown")).replace("_", " ").title()

        # Source header with index number and extracted information
        header = f"[Source {i}] Mission: {mission} | Document: {source} | Category: {category}"
        if metadata.get("distance") is not None:
            header += f" | Distance: {metadata['distance']}"

        # Separator line, header, then the (possibly truncated) text
        context_parts.append("---")
        context_parts.append(header)
        text = (document or "").strip()
        if len(text) > MAX_CONTEXT_CHARS_PER_DOCUMENT:
            text = text[:MAX_CONTEXT_CHARS_PER_DOCUMENT].rstrip() + "..."
        context_parts.append(text)

    return "\n".join(context_parts)
