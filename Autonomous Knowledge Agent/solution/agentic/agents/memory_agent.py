"""Memory agent: loads long-term context before the work, persists what was learned after it."""
from __future__ import annotations

from langchain_core.messages import AIMessage

from agentic.agents.common import decision, latest_user_text
from agentic.db import udahub_session
from agentic.logging_utils import log_event
from agentic.memory import extract_preferences, load_memory, save_preferences, save_resolved_issue
from data.models.udahub import Ticket, TicketMessage, TicketMetadata


def load_memory_node(state):
    mem = load_memory(state["account_id"], state.get("user_id"), state.get("ticket_text", ""), state.get("ticket_id"))
    return {"memory_context": mem, "decision_log": [decision(
        state, "memory", "memory_loaded", known_customer=mem["known_customer"], preferences=list(mem["preferences"]),
        similar_past_issues=len(mem["past_issues"]), prior_tickets=mem["interaction_count"],
        open_escalations=mem["open_escalations"])]}


def finalize_node(state):
    """Persist the reply, ticket status/metadata and long-term memory, then hand the answer back."""
    reply = state.get("draft_response") or "Thanks for contacting CultPass support."
    res = state.get("resolution", {}) or {}
    cls = state.get("classification", {})
    status = {"resolved": "resolved", "awaiting_customer": "awaiting_customer", "escalate": "escalated"}.get(
        res.get("status"), "open")
    agent = "escalation" if status == "escalated" else res.get("resolved_by", "resolver")
    text = state.get("ticket_text", "")
    learned = {}
    with udahub_session() as db:
        t = db.get(Ticket, state["ticket_id"])
        t.status = status
        t.user_id = state.get("user_id") or t.user_id
        meta = db.get(TicketMetadata, state["ticket_id"])
        meta.status, meta.main_issue_type, meta.intent = status, cls.get("category"), cls.get("intent")
        meta.urgency, meta.sentiment, meta.complexity = cls.get("urgency"), cls.get("sentiment"), cls.get("complexity")
        meta.tags = [x for x in (cls.get("category"), cls.get("action"), cls.get("intent")) if x and x != "none"]
        meta.routed_to, meta.confidence = state.get("route"), res.get("confidence")
        if status == "resolved":
            meta.resolved_by = agent
        esc = state.get("escalation") or {}
        if esc:
            meta.escalation_queue, meta.escalation_priority = esc.get("queue"), esc.get("priority")
            meta.escalation_reason = esc.get("reason")
        db.add(TicketMessage(ticket_id=state["ticket_id"], role="assistant", agent=agent, content=reply))
    # ---- long-term memory (only for identified customers) ----
    user_id = state.get("user_id")
    if user_id:
        prefs = extract_preferences(text)
        if prefs:
            save_preferences(state["account_id"], user_id, prefs, state["ticket_id"])
            learned["preferences"] = prefs
        if status == "resolved" and cls.get("intent") in ("question", "account_action"):
            summary = f"[{cls.get('category')}] {text.strip()[:160]} -> {res.get('outcome') or 'answered from KB'}"
            save_resolved_issue(state["account_id"], user_id, state["ticket_id"], summary,
                                [cls.get("category"), cls.get("action")])
            learned["resolved_issue"] = summary
    log_event("ticket_outcome", ticket_id=state["ticket_id"], thread_id=state.get("thread_id"), status=status,
              resolved_by=agent, route=state.get("route"), confidence=res.get("confidence"),
              tools_used=[u["tool"] for u in state.get("tool_usage", [])][-6:], memory_written=list(learned))
    return {"messages": [AIMessage(content=reply, name=agent)], "final_response": reply,
            "decision_log": [decision(state, "memory", "memory_saved", status=status, **learned)]}
