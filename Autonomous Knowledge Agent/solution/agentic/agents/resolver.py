"""Resolver agent: answers ONLY from knowledge-base articles (RAG) and escalates when confidence is low."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from agentic import config
from agentic.agents.common import call_tool, decision, first_name, latest_user_text, previous_user_text
from agentic.llm import get_llm
from agentic.logging_utils import log_event
from agentic.tools.kb_search import best_sentences


class ResolverOutput(BaseModel):
    can_answer: bool
    answer: str
    confidence: float
    used_article_ids: list[str] = []


def _greeting(mem: dict) -> str:
    name = mem.get("preferences", {}).get("preferred_name") or first_name(mem.get("name"))
    return f"Hi {name}," if name else "Hi there,"


def _conversational(state, kind: str):
    mem = state.get("memory_context", {})
    if kind == "smalltalk":
        text = f"{_greeting(mem)} I'm the CultPass support assistant. How can I help you today?"
        if mem.get("interaction_count"):
            text = f"{_greeting(mem)} welcome back! How can I help you today?"
    else:
        text = (f"{_greeting(mem)} I want to make sure I help with the right thing. Could you tell me a bit more, "
                "for example whether it's about a reservation, your subscription, billing or the app?")
    return {"draft_response": text,
            "resolution": {"status": "awaiting_customer", "resolved_by": "resolver", "confidence": 1.0,
                           "reason": kind, "outcome": kind},
            "decision_log": [decision(state, "resolver", f"{kind}_reply")]}


def resolver_node(state):
    cls, mem = state["classification"], state.get("memory_context", {})
    if cls["intent"] in ("smalltalk", "unclear"):
        return _conversational(state, cls["intent"])

    text = latest_user_text(state)
    query = text if len(text.split()) >= 5 else f"{previous_user_text(state)} {text}".strip()
    res, usage = call_tool(state, "resolver", "search_knowledge_base", account_id=state["account_id"], query=query)
    results = (res.get("data") or {}).get("results", [])
    top = results[0] if results else None
    conf = top["confidence"] if top else 0.0
    threshold = config.confidence_threshold()
    base = {"kb_results": [{k: r[k] for k in ("article_id", "title", "score", "coverage", "confidence")} for r in results],
            "tool_usage": [usage]}

    def escalate(reason: str):
        return {**base, "resolution": {"status": "escalate", "resolved_by": "resolver", "confidence": conf,
                                       "reason": reason},
                "decision_log": [decision(state, "resolver", "escalate", reason=reason, confidence=conf,
                                          threshold=threshold, best_article=top["article_id"] if top else None)]}

    if not top:
        return escalate("no relevant knowledge-base article found")
    if conf < threshold:
        return escalate(f"low retrieval confidence {conf:.2f} < {threshold:.2f}")
    if top["coverage"] < config.MIN_COVERAGE:
        return escalate(f"article covers only {top['coverage']:.0%} of the question's terms")

    answer, source = None, "extractive"
    llm = get_llm()
    if llm is not None:
        try:
            context = "\n\n".join(f"[{r['article_id']}] {r['title']}\n{r['content']}" for r in results[:3])
            style = mem.get("preferences", {}).get("response_style", "balanced")
            out = llm.with_structured_output(ResolverOutput).invoke([
                ("system", "You are CultPass customer support. Answer ONLY with facts found in the articles below. "
                           "If they do not contain the answer set can_answer=false. Never invent policies, prices or steps. "
                           f"Reply style: {style}. Do not greet.\n\nARTICLES:\n{context}"),
                ("human", text)])
            if not out.can_answer or out.confidence < 0.5:
                return escalate(f"LLM judged the articles insufficient (can_answer={out.can_answer}, conf={out.confidence:.2f})")
            answer, source = out.answer, "llm"
        except Exception as exc:
            log_event("llm_fallback", agent="resolver", ticket_id=state.get("ticket_id"), error=str(exc)[:200])
    if answer is None:
        style = mem.get("preferences", {}).get("response_style")
        sents = best_sentences(top["content"], query, n=2 if style == "concise" else 99 if style == "detailed" else 3)
        answer = f"According to our help article \"{top['title']}\": " + " ".join(sents)

    parts = [f"{_greeting(mem)}", answer]
    # a past issue was answered with the same article, or is textually similar -> mention it
    related = next((p for p in mem.get("recent_issues", []) if top["title"] in p["summary"]), None) \
        or (mem["past_issues"][0] if mem.get("past_issues") else None)
    if related:
        p = related
        parts.append(f"(I can see you contacted us about something similar on {p['date']}. "
                     "If those steps didn't fix it, tell me and I'll bring in a specialist.)")
    parts.append("Does that answer your question?")
    return {**base, "draft_response": "\n\n".join(parts),
            "resolution": {"status": "resolved", "resolved_by": "resolver", "confidence": conf,
                           "article_ids": [top["article_id"]], "outcome": f"answered from KB: {top['title']}"},
            "decision_log": [decision(state, "resolver", "resolved", confidence=conf, article=top["article_id"],
                                      source=source, personalised=bool(related or mem.get("preferences")))]}
