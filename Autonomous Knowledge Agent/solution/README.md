# UDA-Hub – Universal Decision Agent (LangGraph multi-agent support system)

Multi-agent customer-support system for the **CultPass** account: classifies tickets, routes them (Supervisor pattern),
answers from a knowledge base (RAG), performs account operations through tools, escalates with a hand-off summary,
and remembers customers across sessions. Design + diagrams: [`agentic/design/architecture.md`](agentic/design/architecture.md).

## Run it
```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt                 # versions pinned; developed on Python 3.12.3
cp .env.example .env                            # optional: add OPENAI_API_KEY (and OPENAI_BASE_URL) for LLM mode
jupyter nbconvert --execute --inplace 01_external_db_setup.ipynb 02_core_db_setup.ipynb   # or run them in Jupyter
python 03_agentic_app.py --demo                 # scripted scenarios      (or open 03_agentic_app.ipynb)
python 03_agentic_app.py --user u_alice         # interactive chat as a CultPass customer
python -m pytest -q                             # 34 tests (offline mode, isolated temp DBs)
```
`.db` files and `.env` are intentionally not shipped; notebooks 01/02 (re)create the databases.
Demo customers: `u_alice` (premium), `u_bob` (basic, old payment), `u_dev` (annual plan, refund needs approval),
`u_grace` (recent small payment), `u_erin` (blocked) – emails are `<name>@example.com`.

## Two modes
* **LLM mode** (`OPENAI_API_KEY` set): Classifier and Resolver use structured output; Resolver must answer only from retrieved articles; Escalation polishes the hand-off note.
* **Offline mode** (no key / `UDAHUB_OFFLINE=1`): every agent has a deterministic path (rules + extractive answers). Tests and the executed notebooks use this mode.
Any LLM error falls back to the rule path and logs `llm_fallback`.

## Rubric map
| Requirement | Where |
|---|---|
| DB + KB setup, 6 required tables, ≥10 new articles | `data/models/*`, `data/setup_db.py`, notebooks 01/02, `data/core/cultpass_articles.jsonl` (18 articles, 7 categories), `tests/test_data_setup.py` |
| Architecture doc + diagram | `agentic/design/architecture.md` |
| LangGraph, ≥4 specialised agents, state | `agentic/workflow.py` (hand-built `StateGraph`), `agentic/agents/` (intake, memory, classifier, supervisor, resolver, account_ops, escalation), `agentic/state.py` |
| Routing on content + metadata | `agents/supervisor.decide_route`, `agents/classifier.py` (uses channel, ticket age, history) |
| Knowledge retrieval, confidence, escalation | `tools/kb_search.py`, `agents/resolver.py` |
| ≥2 tools with DB abstraction, errors, validation | `tools/cultpass_db.py` (7 ops), `tools/tools.py`, MCP: `tools/mcp_server.py` |
| Persistent history, short/long-term memory | `memory.py`, `agents/memory_agent.py`, SQLite checkpointer by `thread_id`, `inspect_thread()` |
| End-to-end flow, logging, edge cases | notebook 03, `tests/test_workflow_e2e.py`, `logs/udahub.jsonl` (sample from the notebook run), `logging_utils.search_logs` |

## Notes and limitations (read before grading)
* The starter folder was not available when this was written, so notebooks 01/02, the data models and the 4 "provided" articles (`kb-001`–`kb-004`) are **re-created stand-ins**.
  If you have the official starter data, keep its 4 articles and append kb-005 … kb-018 to `cultpass_articles.jsonl`, and adapt `data/setup_db.py` to its schema.
* The LLM code paths were exercised only with a stub model (unit test); no live OpenAI call was made while building this.
* Retrieval is lexical (TF-IDF + coverage); it can miss paraphrases or match on shared words. The thresholds were tuned on the test queries in `tests/`.
* Chat identity is e-mail based (demo-grade). Real deployments should pass the authenticated `external_user_id`.
* MCP server is provided and imports cleanly, but the workflow calls the same functions in-process.
* Packages: see `requirements.txt` (langgraph 1.2.16, langchain-core 1.6.12, langchain-openai 1.7.2, SQLAlchemy 2.1.5, scikit-learn 1.8.0, fastmcp 4.1.0).
