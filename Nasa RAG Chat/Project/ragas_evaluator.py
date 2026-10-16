"""RAGAS evaluation of the NASA RAG system.

Real-time use (called by ``chat.py`` for every answer)::

    from ragas_evaluator import evaluate_response_quality
    scores = evaluate_response_quality(question, answer, contexts)
    # {'faithfulness': 0.92, 'answer_relevancy': 0.88}

Metrics
-------
Always computed (they only need the question, the retrieved context and the answer):

* ``faithfulness``      - are the claims of the answer supported by the retrieved context?
* ``answer_relevancy``  - does the answer actually address the question? (RAGAS "ResponseRelevancy")

Optional, computed when a reference (expected) answer is passed in:

* ``bleu_score``                              - n-gram overlap with the reference answer
* ``rouge_score``                             - ROUGE-L F-measure with the reference answer
* ``non_llm_context_precision_with_reference`` - share of retrieved chunks that match the reference

Batch use (end-to-end over a test set, see ``evaluation_dataset.txt``)::

    python ragas_evaluator.py --dataset evaluation_dataset.txt --openai-key $OPENAI_API_KEY

Invalid input (empty question/answer/context, wrong types, missing API key) never raises: the
functions return ``{"error": "<clear message>"}`` instead.
"""

import argparse
import json
import logging
import math
import os
import re
import sys
import types
from pathlib import Path
from typing import Any, Dict, List, Optional

import warnings

# RAGAS 0.4 and LangChain print deprecation notices for the wrapper classes this project uses
# (they still work and are what the course material uses). Hide just those notices.
for _pattern in (r".*is deprecated.*", r".*being sunset.*"):
    warnings.filterwarnings("ignore", message=_pattern, category=DeprecationWarning)

from openai_utils import DEFAULT_EMBEDDING_MODEL, get_api_key_from_env, resolve_base_url

logger = logging.getLogger(__name__)

# Models used by the evaluator (the LLM judges faithfulness / relevancy).
EVALUATOR_MODEL = os.getenv("RAGAS_EVALUATOR_MODEL", "gpt-3.5-turbo")
EVALUATOR_EMBEDDING_MODEL = DEFAULT_EMBEDDING_MODEL

# Names of the metrics returned by this module.
REFERENCE_FREE_METRICS = ("faithfulness", "answer_relevancy")
REFERENCE_BASED_METRICS = ("bleu_score", "rouge_score", "non_llm_context_precision_with_reference")


def _ensure_ragas_vertexai_compat() -> None:
    """Work around the RAGAS 0.4.3 / LangChain VertexAI import error.

    RAGAS 0.4.3 imports ``ChatVertexAI`` and ``VertexAI`` from old ``langchain_community`` paths
    that no longer exist in recent LangChain releases (``ImportError: cannot import name
    'ChatVertexAI'``). Instead of asking everybody to edit files inside ``site-packages`` (see the
    README), the classes are made available under the old import paths before RAGAS is imported.
    """
    try:
        import langchain_community.chat_models.vertexai  # noqa: F401
        return  # nothing to do: the old path still exists
    except Exception:
        pass

    try:
        from langchain_google_vertexai import ChatVertexAI, VertexAI
    except Exception:
        return  # not installed - the RAGAS import below reports the real problem

    shim = types.ModuleType("langchain_community.chat_models.vertexai")
    shim.ChatVertexAI = ChatVertexAI
    sys.modules["langchain_community.chat_models.vertexai"] = shim
    try:
        import langchain_community.chat_models as chat_models_module
        chat_models_module.vertexai = shim
    except Exception:
        pass
    try:
        import langchain_community.llms as llms_module
        llms_module.VertexAI = VertexAI
    except Exception:
        pass


_ensure_ragas_vertexai_compat()

# RAGAS imports
RAGAS_IMPORT_ERROR: Optional[str] = None
try:
    from ragas import EvaluationDataset, SingleTurnSample, evaluate
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import (
        BleuScore,
        Faithfulness,
        NonLLMContextPrecisionWithReference,
        ResponseRelevancy,
        RougeScore,
    )
    from ragas.run_config import RunConfig
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    RAGAS_AVAILABLE = True
except Exception as import_error:  # ImportError, but also errors raised while importing
    RAGAS_AVAILABLE = False
    RAGAS_IMPORT_ERROR = f"{type(import_error).__name__}: {import_error}"


# ----------------------------------------------------------------------------------------
# Input validation
# ----------------------------------------------------------------------------------------
def _validate_inputs(question: Any, answer: Any, contexts: Any) -> Optional[str]:
    """Return a human readable error message if the inputs cannot be evaluated, else None."""
    if not isinstance(question, str) or not question.strip():
        return "Invalid input: the question must be a non-empty string."
    if not isinstance(answer, str) or not answer.strip():
        return "Invalid input: the answer must be a non-empty string."
    if not isinstance(contexts, (list, tuple)):
        return "Invalid input: contexts must be a list of strings."
    if not all(isinstance(item, str) for item in contexts):
        return "Invalid input: every context item must be a string."
    if not any(item.strip() for item in contexts):
        return "Invalid input: no retrieved context was provided, so the answer cannot be evaluated."
    return None


def _is_valid_score(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and not math.isnan(value)


# ----------------------------------------------------------------------------------------
# Single (question, context, answer) evaluation
# ----------------------------------------------------------------------------------------
def evaluate_response_quality(question: str, answer: str, contexts: List[str],
                              reference: Optional[str] = None,
                              api_key: Optional[str] = None) -> Dict[str, float]:
    """Evaluate response quality using RAGAS metrics

    Args:
        question: The user's question.
        answer: The answer produced by the RAG system.
        contexts: The retrieved chunks that were given to the LLM.
        reference: Optional expected answer. When given, BLEU, ROUGE and the non-LLM context
                   precision are computed in addition to faithfulness and answer relevancy.
        api_key: OpenAI API key (defaults to CHROMA_OPENAI_API_KEY / OPENAI_API_KEY).

    Returns:
        ``{metric_name: score}`` with scores between 0 and 1, e.g.
        ``{"faithfulness": 0.9, "answer_relevancy": 0.85}``.
        On problems a dict with a single ``"error"`` key is returned instead of raising.
    """
    if not RAGAS_AVAILABLE:
        return {"error": f"RAGAS not available ({RAGAS_IMPORT_ERROR}). Install with: pip install ragas"}

    validation_error = _validate_inputs(question, answer, contexts)
    if validation_error:
        return {"error": validation_error}

    key = api_key or get_api_key_from_env()
    if not key:
        return {"error": "An OpenAI API key is required for evaluation "
                         "(set OPENAI_API_KEY or enter it in the app)."}

    clean_contexts = [item.strip() for item in contexts if item.strip()]
    has_reference = isinstance(reference, str) and bool(reference.strip())

    try:
        base_url = resolve_base_url(key)

        # Create evaluator LLM with model gpt-3.5-turbo (judges faithfulness and relevancy)
        evaluator_llm = LangchainLLMWrapper(ChatOpenAI(
            model=EVALUATOR_MODEL, api_key=key, base_url=base_url, temperature=0
        ))

        # Create evaluator embeddings with model text-embedding-3-small
        evaluator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(
            model=EVALUATOR_EMBEDDING_MODEL, api_key=key, base_url=base_url,
            check_embedding_ctx_length=False  # send plain text: works with every OpenAI-compatible endpoint
        ))

        # Define an instance for each metric to evaluate
        metrics = [Faithfulness(), ResponseRelevancy()]
        if has_reference:
            # Optional metrics need extra packages (sacrebleu, rouge-score, rapidfuzz). If one is
            # missing it is skipped with a warning so the two core metrics are still returned.
            for factory in (BleuScore,
                            lambda: RougeScore(rouge_type="rougeL", mode="fmeasure"),
                            NonLLMContextPrecisionWithReference):
                try:
                    metrics.append(factory())
                except Exception as metric_error:
                    logger.warning(f"Skipping an optional metric: {metric_error}")

        sample_fields: Dict[str, Any] = {
            "user_input": question.strip(),
            "response": answer.strip(),
            "retrieved_contexts": clean_contexts,
        }
        if has_reference:
            sample_fields["reference"] = reference.strip()
            sample_fields["reference_contexts"] = [reference.strip()]
        dataset = EvaluationDataset(samples=[SingleTurnSample(**sample_fields)])

        # Evaluate the response using the metrics
        result = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=evaluator_llm,
            embeddings=evaluator_embeddings,
            run_config=RunConfig(timeout=120, max_retries=3, max_workers=4),
            show_progress=False,
            raise_exceptions=False,
        )
        raw_scores = result.scores[0] if result.scores else {}
    except Exception as e:
        logger.exception("RAGAS evaluation failed")
        return {"error": f"Evaluation failed: {e}"}

    # Return the evaluation results (metrics that could not be computed are left out)
    scores: Dict[str, float] = {}
    for name, value in raw_scores.items():
        clean_name = re.sub(r"\(.*\)$", "", name)  # "rouge_score(mode=fmeasure)" -> "rouge_score"
        if _is_valid_score(value):
            scores[clean_name] = round(float(value), 4)
        else:
            logger.warning(f"Metric '{name}' could not be computed for this answer")

    if not scores:
        return {"error": "RAGAS returned no valid scores. Check the API key, the model access "
                         "and the application log."}
    return scores


# ----------------------------------------------------------------------------------------
# Batch evaluation
# ----------------------------------------------------------------------------------------
def aggregate_scores(per_item_scores: List[Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """Mean / min / max / count for every metric across several evaluated items."""
    values_by_metric: Dict[str, List[float]] = {}
    for scores in per_item_scores:
        for name, value in (scores or {}).items():
            if name != "error" and _is_valid_score(value):
                values_by_metric.setdefault(name, []).append(float(value))

    return {
        name: {
            "mean": round(sum(values) / len(values), 4),
            "min": round(min(values), 4),
            "max": round(max(values), 4),
            "count": len(values),
        }
        for name, values in values_by_metric.items()
    }


def evaluate_batch(items: List[Dict[str, Any]], api_key: Optional[str] = None,
                   with_reference_metrics: bool = False) -> Dict[str, Any]:
    """Evaluate many (question, answer, contexts[, reference]) items.

    Each item is a dict with the keys ``question``, ``answer``, ``contexts`` and optionally
    ``reference``. Items that cannot be evaluated get an ``error`` entry instead of scores.

    Returns:
        ``{"results": [...per item...], "aggregate": {metric: {mean, min, max, count}}}``
    """
    results = []
    for position, item in enumerate(items, start=1):
        scores = evaluate_response_quality(
            item.get("question"), item.get("answer"), item.get("contexts"),
            reference=item.get("reference") if with_reference_metrics else None,
            api_key=api_key,
        )
        results.append({**{k: v for k, v in item.items() if k not in ("contexts",)},
                        "n_contexts": len(item.get("contexts") or []),
                        "scores": scores})
        logger.info(f"Evaluated {position}/{len(items)}: {scores}")

    return {
        "results": results,
        "aggregate": aggregate_scores([r["scores"] for r in results]),
    }


def load_test_questions(path: str) -> List[Dict[str, str]]:
    """Load the evaluation questions from ``evaluation_dataset.txt`` or a ``.json`` file.

    Text format - blocks separated by a line containing only ``---``; each block has the fields
    ``ID``, ``CATEGORY``, ``MISSION``, ``QUESTION`` and ``EXPECTED_ANSWER`` (the expected answer
    may continue over several lines). Lines starting with ``#`` are comments.

    JSON format - a list of objects (or ``{"questions": [...]}``) using the same field names in
    lower case (``id``, ``category``, ``mission``, ``question``, ``expected_answer``).

    Returns:
        A list of dicts with the lower-case keys ``id``, ``category``, ``mission``, ``question``
        and ``expected_answer``.

    Raises:
        FileNotFoundError / ValueError with a clear message for missing or malformed files.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Evaluation dataset not found: {path}")

    raw_text = file_path.read_text(encoding="utf-8")
    entries: List[Dict[str, str]] = []

    if file_path.suffix.lower() == ".json":
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"{path} is not valid JSON: {e}") from e
        if isinstance(data, dict):
            data = data.get("questions", [])
        if not isinstance(data, list):
            raise ValueError(f"{path} must contain a list of questions")
        for index, entry in enumerate(data, start=1):
            if not isinstance(entry, dict):
                raise ValueError(f"Entry {index} of {path} is not an object")
            entries.append({str(k).lower(): str(v) for k, v in entry.items()})
    else:
        field_pattern = re.compile(r"^(ID|CATEGORY|MISSION|QUESTION|EXPECTED_ANSWER)\s*:\s*(.*)$")
        current: Dict[str, str] = {}
        current_field: Optional[str] = None

        def finish_block() -> None:
            nonlocal current, current_field
            if current:
                entries.append({k: v.strip() for k, v in current.items()})
            current, current_field = {}, None

        for line in raw_text.splitlines():
            if line.strip() == "---":
                finish_block()
                continue
            if line.lstrip().startswith("#") and current_field is None:
                continue
            match = field_pattern.match(line)
            if match:
                current_field = match.group(1).lower()
                current[current_field] = match.group(2)
            elif current_field and line.strip():
                current[current_field] += " " + line.strip()
        finish_block()

    questions = []
    for index, entry in enumerate(entries, start=1):
        if not entry.get("question", "").strip():
            raise ValueError(f"Entry {index} of {path} has no QUESTION")
        questions.append({
            "id": entry.get("id", str(index)),
            "category": entry.get("category", "general"),
            "mission": entry.get("mission", "all"),
            "question": entry["question"].strip(),
            "expected_answer": entry.get("expected_answer", ""),
        })
    if not questions:
        raise ValueError(f"No questions found in {path}")
    return questions


def run_batch_evaluation(dataset_path: str, chroma_dir: str, collection_name: str,
                         api_key: str, model: str = "gpt-3.5-turbo", n_results: int = 8,
                         with_reference_metrics: bool = False,
                         limit: Optional[int] = None,
                         query_expansion: bool = True) -> Dict[str, Any]:
    """End-to-end evaluation: retrieve -> generate an answer -> score it, for every test question.

    Returns the same structure as :func:`evaluate_batch`, plus the dataset path and settings.
    """
    # imported here so that single-answer evaluation does not depend on the other components
    import llm_client
    import rag_client

    questions = load_test_questions(dataset_path)
    if limit:
        questions = questions[:limit]

    collection, ok, error = rag_client.initialize_rag_system(chroma_dir, collection_name)
    if not ok:
        raise RuntimeError(f"Could not open collection '{collection_name}' in '{chroma_dir}': {error}. "
                           f"Run embedding_pipeline.py first.")

    items = []
    for question in questions:
        try:
            expansion = (llm_client.expand_query(api_key, question["question"], [], model)
                         if query_expansion else "")
            retrieved = rag_client.retrieve_documents(
                collection, question["question"], n_results=n_results,
                mission_filter=question["mission"], api_key=api_key,
                query_expansion=expansion,
            )
            documents = retrieved["documents"][0] if retrieved else []
            metadatas = retrieved["metadatas"][0] if retrieved else []
            context = rag_client.format_context(documents, metadatas)
            answer = llm_client.generate_response(api_key, question["question"], context, [], model)
        except Exception as e:
            logger.error(f"Question {question['id']} failed: {e}")
            documents, answer = [], ""
        items.append({
            "id": question["id"],
            "category": question["category"],
            "mission": question["mission"],
            "question": question["question"],
            "answer": answer,
            "contexts": documents,
            "reference": question["expected_answer"],
        })

    report = evaluate_batch(items, api_key=api_key, with_reference_metrics=with_reference_metrics)
    report.update({
        "dataset": dataset_path,
        "collection": collection_name,
        "chat_model": model,
        "evaluator_model": EVALUATOR_MODEL,
        "n_results": n_results,
    })
    return report


def print_report(report: Dict[str, Any]) -> None:
    """Print a per-question summary and the aggregate score of each metric."""
    print("\n" + "=" * 78)
    print("RAGAS EVALUATION REPORT")
    print("=" * 78)
    print(f"Dataset: {report.get('dataset', '-')}   Chat model: {report.get('chat_model', '-')}   "
          f"Evaluator: {report.get('evaluator_model', '-')}")

    print("\nPer question:")
    for result in report["results"]:
        scores = result["scores"]
        if "error" in scores:
            score_text = f"ERROR - {scores['error']}"
        else:
            score_text = "  ".join(f"{name}={value:.3f}" for name, value in scores.items())
        print(f"  [{result.get('id', '?'):>2}] {result.get('category', ''):<16} "
              f"{result.get('mission', ''):<10} {score_text}")
        print(f"       Q: {result.get('question', '')[:90]}")

    print("\nAggregate over all questions:")
    if not report["aggregate"]:
        print("  (no scores could be computed)")
    for name, stats in report["aggregate"].items():
        print(f"  {name:<42} mean={stats['mean']:.3f}  min={stats['min']:.3f}  "
              f"max={stats['max']:.3f}  (n={stats['count']})")
    print("=" * 78)


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch RAGAS evaluation of the NASA RAG system")
    parser.add_argument("--dataset", default="evaluation_dataset.txt",
                        help="Test questions (evaluation_dataset.txt or a .json file)")
    parser.add_argument("--openai-key", default=None, help="OpenAI API key (default: environment)")
    parser.add_argument("--chroma-dir", default="./chroma_db_openai", help="ChromaDB directory")
    parser.add_argument("--collection-name", default="nasa_space_missions_text", help="Collection name")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="Chat model that writes the answers")
    parser.add_argument("--n-results", type=int, default=8, help="Chunks retrieved per question")
    parser.add_argument("--no-query-expansion", action="store_true",
                        help="Search with the plain question only (no LLM query expansion)")
    parser.add_argument("--with-reference-metrics", action="store_true",
                        help="Also compute BLEU, ROUGE and context precision against the expected answers")
    parser.add_argument("--limit", type=int, default=None, help="Only evaluate the first N questions")
    parser.add_argument("--output", default="evaluation_results.json", help="Where to save the JSON report")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)  # one line per API request is just noise

    api_key = args.openai_key or get_api_key_from_env()
    if not api_key:
        parser.error("an OpenAI API key is required: pass --openai-key or set OPENAI_API_KEY")
    if not RAGAS_AVAILABLE:
        parser.error(f"RAGAS is not available: {RAGAS_IMPORT_ERROR}")

    try:
        report = run_batch_evaluation(
            args.dataset, args.chroma_dir, args.collection_name, api_key,
            model=args.model, n_results=args.n_results,
            with_reference_metrics=args.with_reference_metrics, limit=args.limit,
            query_expansion=not args.no_query_expansion,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    print_report(report)
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Full report saved to {args.output}")


if __name__ == "__main__":
    main()
