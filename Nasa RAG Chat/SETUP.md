# Setup and Testing Guide

You need **Python 3.10+** and an **OpenAI API key** (Udacity/Vocareum keys starting with `voc` also work and are detected automatically).

## 1. Open a terminal in this folder

```bash
cd nasa-rag-chat
```

## 2. Create a virtual environment and install packages

Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Set your API key

Mac/Linux: `export OPENAI_API_KEY="your-key-here"`
Windows (PowerShell): `$env:OPENAI_API_KEY="your-key-here"`

## 4. Check that everything imports

```bash
python -c "import ragas_evaluator; print('RAGAS ok:', ragas_evaluator.RAGAS_AVAILABLE)"
```

Expected: `RAGAS ok: True`. If it prints `False`, the message shows what is missing; re-run step 2.

## 5. Build the vector database (run once)

```bash
python embedding_pipeline.py --data-path ./data_text
```

Creates about 16,500 chunks and takes a few minutes. It finishes with `Errors: 0`. For a cheaper
trial, add `--chunk-size 1000 --chunk-overlap 200` (roughly half the chunks).

Inspect the result (no API key needed):

```bash
python embedding_pipeline.py --stats-only
```

Expected: `collection_size (chunks): ~16558` and counts for `apollo_11`, `apollo_13`, `challenger`.

Optional checks:
```bash
python embedding_pipeline.py --test-query "What caused the Apollo 13 accident?"
python embedding_pipeline.py                        # re-run: everything skipped, no API cost
python embedding_pipeline.py --update-mode replace  # rebuild each file from scratch
```

## 6. Launch the chat app

```bash
streamlit run chat.py
```

Opens at http://localhost:8501. Try:

| Question | Mission focus | Expect |
|---|---|---|
| What problems did Apollo 13 encounter? | Apollo 13 | Oxygen tank failure, loss of power, Aquarius lifeboat |
| Who were the Apollo 11 crew members? | Apollo 11 | Armstrong, Collins, Aldrin, with `[Source n]` citations |
| What was the last call before the Challenger accident? | Challenger | "Go at throttle up" |
| What were the objectives of Columbia STS-107? | All missions | A statement that the archive has no information |
| "And who was the commander?" (follow-up) | any | Uses the earlier turns |

For each answer check: the **Sources used** expander lists chunks from the right mission, and
**Faithfulness** and **Answer Relevancy** appear in the sidebar (0.8+ is good).

## 7. Run the batch evaluation

```bash
python ragas_evaluator.py --dataset evaluation_dataset.txt
```

Answers all 14 test questions, prints a per-question table and the mean/min/max of each metric, and
saves `evaluation_results.json`. Use `--limit 3` for a cheaper run and `--with-reference-metrics`
to add BLEU, ROUGE and context precision.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `No ChromaDB backends found` | Run step 5 first, from the same folder as `chat.py` |
| `Collection ... does not exist` | `--chroma-dir` / `--collection-name` differ between pipeline and app |
| `RAGAS ok: False` | Re-run `pip install -r requirements.txt` and read the printed error |
| Evaluation error in the sidebar | Check the key can use `gpt-3.5-turbo`, or set `RAGAS_EVALUATOR_MODEL` to a model it can use |
| Rate-limit messages while embedding | Normal; it retries automatically. If it keeps failing, re-run: `skip` mode resumes where it stopped |
