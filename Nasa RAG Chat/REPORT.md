# Project Report: NASA Mission Intelligence Chat

## What was built

A complete RAG application: an embedding pipeline (chunking, OpenAI embeddings, ChromaDB), a retrieval
client with mission filtering, an LLM client with a grounded NASA-expert prompt and conversation
history, a RAGAS evaluator (single answer and batch), and a Streamlit chat app that shows sources
and live quality scores. All TODO items in `llm_client.py`, `rag_client.py`,
`embedding_pipeline.py`, `ragas_evaluator.py` and `chat.py` are implemented.

## Key decisions

* **Exact chunk guarantees.** Chunks are cut on sentence/line boundaries where possible but never
  exceed `chunk_size`, and the overlap between consecutive chunks is exactly `chunk_overlap`.
  Offsets (`chunk_start`, `chunk_end`) are stored so every chunk can be traced back to its file.
* **Idempotent ingestion.** Stable IDs (`mission_source_chunk_0001`) make re-runs safe. `skip` costs
  no API calls, `update` re-embeds and removes stale chunks when the chunking changed, and `replace`
  rebuilds each file from scratch.
* **Cost and reliability.** Embeddings are requested in batches of 50 (one request instead of 50) with
  exponential back-off on rate limits and timeouts. A failure in one file is logged and the rest
  continue; re-running resumes where it stopped.
* **Embedding model stored with the collection.** The query side reads the model name from the
  collection metadata, so questions are always embedded with the same model as the documents.
* **Over-fetch then de-duplicate.** Retrieval asks Chroma for 3x the requested chunks, sorts by
  distance and drops repeated/contained snippets, so the user still gets `k` distinct chunks, which
  matters because overlapping chunks are near-duplicates.
* **Grounding.** The system prompt forbids facts outside the context, requires `[Source n]`
  citations and an explicit "not enough information" answer; temperature is 0.2.

## Challenges and solutions

| Challenge | Solution |
|---|---|
| RAGAS 0.4.3 fails to import (`ChatVertexAI`) with current LangChain; the instructions say to edit files in `site-packages` | `ragas_evaluator.py` registers the classes under the old import paths before importing RAGAS, so no manual edit is needed |
| Reference-based metrics need `rapidfuzz`, `rouge-score`, `sacrebleu`, which were not in `requirements.txt` | Added to `requirements.txt`; the evaluator skips an optional metric with a warning rather than failing |
| RAGAS names ROUGE `rouge_score(mode=fmeasure)` | Metric names are normalized to `rouge_score` |
| Streamlit requires `set_page_config` to be the first Streamlit call | The RAGAS-availability warning moved into `main()` |
| Overlapping chunks make retrieval return near-identical text | Distance sort + containment de-duplication |
| Transcripts use phonetic names ("Scobie", "Resnick") | Documented; the expected answers in `evaluation_dataset.txt` use the usual spellings and note the difference |

## Testing performed

**Development tests (stub server).** The build environment had no OpenAI access, so the code was first
tested against a local OpenAI-compatible stub with the real NASA files: chunking property tests (no chunk
over the size, exact overlap, full coverage; 300 random cases), a full pipeline run, the three update modes,
`--stats-only`, `--delete-source`, retries after injected HTTP 429 errors, retrieval (top-k, mission filter,
de-duplication), the evaluator with malformed input, and the Streamlit app with its test harness.

**Real run (Udacity OpenAI endpoint).** The database was built from the 12 files (16,558 chunks, 500/100,
`text-embedding-3-small`, 0 errors), the chat app was used interactively, and the batch evaluation
(`python ragas_evaluator.py --model gpt-4o-mini`) was run on the 14 questions of `evaluation_dataset.txt`
(8 chunks per question, query expansion on, evaluator `gpt-3.5-turbo`). The full output is in
`evaluation_results.json`.

| ID | Category | Mission | Faithfulness | Answer relevancy | Outcome |
|---|---|---|---|---|---|
| 1 | overview | apollo_11 | 0.91 | 0.60 | answered |
| 2 | overview | apollo_13 | 0.83 | 0.00 | refused (no answer found) |
| 3 | emergency | apollo_13 | 1.00 | 0.93 | answered |
| 4 | disaster_analysis | challenger | 1.00 | 0.68 | answered |
| 5 | disaster_analysis | challenger | 0.50 | 0.00 | refused (no answer found) |
| 6 | crew | apollo_11 | 0.80 | 0.94 | answered |
| 7 | crew | apollo_13 | 0.33 | 0.85 | answered |
| 8 | crew | challenger | 1.00 | 0.94 | answered |
| 9 | technical | apollo_11 | 0.33 | 0.86 | answered |
| 10 | technical | apollo_13 | 1.00 | 1.00 | answered |
| 11 | timeline | apollo_11 | 1.00 | 0.00 | answered |
| 12 | timeline | apollo_13 | 0.67 | 0.00 | refused (no answer found) |
| 13 | timeline | challenger | 1.00 | 0.00 | answered |
| 14 | out_of_scope | all | 0.00 | 0.00 | correct refusal (not in archive) |

**Aggregate:** faithfulness mean 0.741 (min 0.00, max 1.00);
answer relevancy mean 0.486 (min 0.00, max 1.00); n = 14.

## Findings and limitations

* **Works well:** crew questions (Apollo 11, Apollo 13, Challenger), the Apollo 13 carbon dioxide fix, the Apollo 13
  problems question, and a correct refusal for the out-of-scope Columbia STS-107 question.
* **Retrieval misses.** Overview and timeline questions (IDs 2, 5, 12) were answered with "the excerpts do not contain
  enough information" even though the facts exist in the files. The chunks are 500 characters of radio chatter, and
  a broad question does not look like the passages that answer it. Mission auto-detection, query expansion and 8
  chunks per question helped (the Apollo 13 problems question changed from a refusal to a good answer) but did not
  remove the problem.
* **Grounding slips.** The model sometimes adds detail that is not in the sources: it labelled the 8:32 a.m. launch time
  as EDT although the transcripts give it in CDT (the correct launch time is 9:32 EDT), it wrote "German measles" where
  the source says "measles", and an early run stated "73 seconds" which is not in the archive. The system prompt was
  tightened afterwards (numbers must come from a source; keep time zones as written), but this is a known weakness of
  smaller chat models.
* **Metric behaviour.** RAGAS scores a refusal, or an answer that ends with "the context does not cover X", as 0 for
  answer relevancy. The correct refusal for the Columbia question therefore scores 0.00 on both metrics, and the long
  Challenger timeline answer scores 0.00 relevancy because of its closing disclaimer. The judge model (`gpt-3.5-turbo`,
  as specified) is noisy, and 14 questions are a small sample, so single scores should not be over-interpreted.
* **Ideas not implemented:** larger chunks (for example 1000/200) in a second collection to compare, hybrid
  keyword + vector search for dates and times, a stronger judge model, and re-ranking of the retrieved chunks.
