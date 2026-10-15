# NASA Mission Intelligence Chat (RAG + RAGAS)

A Retrieval-Augmented Generation system that answers questions about **Apollo 11, Apollo 13 and the
Challenger (STS-51L)** missions from NASA's own transcripts and technical documents, and scores every
answer in real time with **RAGAS**.

```
data_text/*.txt ──► embedding_pipeline.py ──► ChromaDB (chroma_db_openai/)
                                                    │
 question ──► rag_client.py (embed, top-k, mission filter, dedupe, context)
                                                    │
              llm_client.py (NASA-expert prompt + history + context) ──► answer
                                                    │
              ragas_evaluator.py (faithfulness, answer relevancy, ...) ──► scores
                                                    │
                                    chat.py (Streamlit UI)
```

## Project structure

| File | Purpose |
|---|---|
| `embedding_pipeline.py` | Chunks the text files, creates OpenAI embeddings, stores them in ChromaDB (CLI) |
| `rag_client.py` | Discovers/opens ChromaDB collections, semantic retrieval, context formatting |
| `llm_client.py` | System prompt, conversation history, OpenAI chat call |
| `ragas_evaluator.py` | RAGAS metrics for one answer, plus batch evaluation over a test set (CLI) |
| `chat.py` | Streamlit chat application |
| `openai_utils.py` | Shared OpenAI client creation (API key / endpoint handling) |
| `evaluation_dataset.txt` | 14 test questions with expected answers (also `test_questions.json`) |
| `SETUP.md` | Step-by-step setup and testing guide |
| `evaluation_results.json` | Output of a real batch evaluation run (answers and RAGAS scores) |
| `REPORT.md` | Short project report: design decisions, challenges, testing |
| `data_text/` | The NASA source documents (apollo11, apollo13, challenger) |

## Setup

Requires Python 3.10+ and an OpenAI API key.

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key-here"
```

Udacity/Vocareum keys (starting with `voc`) are detected automatically and sent to
`https://openai.vocareum.com/v1`. To use another OpenAI-compatible endpoint, set `OPENAI_BASE_URL`.

> **RAGAS 0.4.3 / VertexAI import error.** RAGAS 0.4.3 fails to import with
> `cannot import name 'ChatVertexAI'` on recent LangChain versions. `ragas_evaluator.py` fixes this
> automatically at import time (no need to edit files in `site-packages`). If you prefer the manual
> fix from the course instructions, it still works and the automatic fix steps aside.

## Usage

### 1. Build the vector database (run once)

```bash
python embedding_pipeline.py --openai-key $OPENAI_API_KEY --data-path ./data_text
```

With the default settings this produces about 16,500 chunks of at most 500 characters.
Options:

| Flag | Default | Meaning |
|---|---|---|
| `--data-path` | `./data_text` | Folder containing `apollo11/`, `apollo13/`, `challenger/` |
| `--chroma-dir` | `./chroma_db_openai` | Where ChromaDB persists the collection |
| `--collection-name` | `nasa_space_missions_text` | Collection name |
| `--embedding-model` | `text-embedding-3-small` | OpenAI embedding model |
| `--chunk-size` | `500` | Maximum characters per chunk (never exceeded) |
| `--chunk-overlap` | `100` | Characters shared by consecutive chunks (exact) |
| `--batch-size` | `50` | Chunks embedded per API request |
| `--update-mode` | `skip` | `skip` existing chunks, `update` them in place, or `replace` all chunks of each file |
| `--stats-only` | | Print collection size and breakdowns by mission / source / category (no API key needed) |
| `--test-query` | | Run a sample similarity query after processing |
| `--delete-source` | | Delete the chunks of sources whose name contains this text |

Examples:

```bash
python embedding_pipeline.py --stats-only
python embedding_pipeline.py --chunk-size 800 --chunk-overlap 150 --update-mode replace
python embedding_pipeline.py --test-query "What caused the Apollo 13 accident?"
```

Every chunk is stored with metadata: `source`, `file_path`, `mission` (`apollo_11`, `apollo_13`,
`challenger`), `data_type`, `document_category`, `chunk_index`, `total_chunks`, `chunk_start`,
`chunk_end`, and more. Chunk IDs follow `mission_source_chunk_0001`, so re-runs are idempotent.

Embeddings are created in batches, with automatic retries on rate limits and timeouts.

### 2. Chat

```bash
streamlit run chat.py
```

In the sidebar choose the collection, API key, chat model, **mission focus** (*Auto-detect from question* by default, which searches only the mission named in your question; or all missions, or one),
the number of chunks to retrieve (top-k) and whether to show RAGAS scores. Each answer is shown with
its sources; the scores appear in the sidebar.

### 3. Evaluate on the test set

```bash
python ragas_evaluator.py --dataset evaluation_dataset.txt
python ragas_evaluator.py --dataset test_questions.json --with-reference-metrics --limit 5
```

This retrieves, answers and scores every question, prints a per-question summary plus the
mean/min/max of each metric, and saves everything to `evaluation_results.json`.

Metrics:

* **faithfulness** and **answer_relevancy** (RAGAS *ResponseRelevancy*): always computed.
* **bleu_score**, **rouge_score**, **non_llm_context_precision_with_reference**: added with
  `--with-reference-metrics`, which compares against each question's `EXPECTED_ANSWER`.

Single answers can be scored from Python:

```python
from ragas_evaluator import evaluate_response_quality
evaluate_response_quality("What went wrong on Apollo 13?", "An oxygen tank failed.", ["...retrieved chunk..."])
# {'faithfulness': 1.0, 'answer_relevancy': 0.87}
```

Invalid input (empty question/answer/context, wrong types, missing key) returns
`{"error": "<clear message>"}` instead of raising.

## Design notes

* **Chunking** is character based and breaks on paragraph / line / sentence boundaries when it can.
  A chunk never exceeds `--chunk-size`, and consecutive chunks overlap by exactly `--chunk-overlap`
  characters. `chunk_overlap` must be smaller than `chunk_size`.
* **Retrieval** embeds the question with the same model that built the collection (stored in the
  collection metadata), queries ChromaDB with cosine distance, optionally filters on `mission`, then
  sorts by similarity and removes repeated or contained snippets, so you get `k` distinct chunks.
* **Query expansion** (on by default in the app, `--no-query-expansion` in the batch evaluator): before
  searching, the chat model rewrites the question into archive-style terms (names, equipment, call
  signs). Broad questions such as "What problems did Apollo 13 encounter?" don't resemble the passages
  that answer them, so the expansion is embedded together with the question. If the rewrite fails, the
  plain question is used.
* **Context** is one string with `---` separators, and every chunk is labelled
  `[Source n] Mission | Document | Category`.
* **Prompt** positions the model as a NASA mission expert, requires inline `[Source n]` citations,
  forbids facts outside the context, and tells it to say so when the context is insufficient.
  Only the last 8 conversation turns are sent, plus the current context.
* The transcripts use phonetic spellings (e.g. "Scobie", "Resnick"), so names in answers may
  differ from the usual spelling.

## Rubric checklist

| Rubric item | Where |
|---|---|
| Configurable chunk size / overlap, never exceeded, consistent overlap | `--chunk-size`, `--chunk-overlap`, `chunk_text()` |
| OpenAI embeddings + per-chunk metadata (source, mission) | `get_embeddings_batch()`, `process_text_file()` |
| `--update-mode` skip / update / replace | `add_documents_to_collection()` |
| Persisted ChromaDB at `--chroma-dir` / `--collection-name`; `--stats-only` | `embedding_pipeline.py` |
| Semantic retrieval, top-k at runtime, mission metadata filter | `rag_client.retrieve_documents()` |
| Clean context with separators + source attribution, dedupe / sort by score | `retrieve_documents()`, `format_context()` |
| System prompt as NASA expert citing sources; history (role + content) | `llm_client.py` |
| Grounded answers, uncertainty when context is insufficient | `SYSTEM_PROMPT` |
| RAGAS Response Relevancy + Faithfulness per answer; extra metrics | `ragas_evaluator.py` |
| (question, context, answer) in, structured result out; errors do not crash | `evaluate_response_quality()` |
| Batch evaluation with per-question summary and aggregates | `ragas_evaluator.py --dataset ...` |
| Evaluation dataset with 5+ questions across categories | `evaluation_dataset.txt`, `test_questions.json` |

## Troubleshooting

* **"No ChromaDB backends found"**: run the embedding pipeline first.
* **`Collection ... does not exist`**: check `--chroma-dir` and `--collection-name` match between
  the pipeline and the app. The app looks for folders containing "chroma" next to `chat.py`.
* **Evaluation shows an error**: check the API key and that the evaluator model
  (`gpt-3.5-turbo` by default, override with `RAGAS_EVALUATOR_MODEL`) is available to your key.
* **Slow first run**: embedding about 16,500 chunks takes a few minutes. Re-runs skip existing chunks.
