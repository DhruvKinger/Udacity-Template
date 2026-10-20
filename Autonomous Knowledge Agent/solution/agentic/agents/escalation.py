"""Escalation agent: builds a hand-off summary for a human, sets priority/queue, tells the customer what happens next."""
from __future__ import annotations

from agentic.agents.common import decision, first_name
from agentic.db import udahub_session
from agentic.llm import get_llm
from agentic.logging_utils import log_event
from data.models.udahub import TicketMessage

SLA = {"P1": "within 1 hour", "P2": "within 4 business hours", "P3": "within 1 business day"}


def priority_and_queue(cls: dict, memory: dict, reason: str) -> tuple[str, str]:
    if cls.get("security_risk"):
        return "P1", "trust_and_safety"
    if cls.get("legal_risk"):
        return "P1", "legal_and_compliance"
    prio = "P2" if (cls.get("urgency") in ("high", "critical") or cls.get("sentiment") == "angry"
                    or memory.get("open_escalations", 0) >= 1 or "refund" in reason) else "P3"
    queue = {"billing": "billing_team", "technical": "technical_support", "account": "account_support",
             "subscription": "account_support", "reservations": "account_support",
             "experiences": "partner_experiences"}.get(cls.get("category"), "general_support")
    return prio, queue


def escalation_node(state):
    cls, mem = state["classification"], state.get("memory_context", {})
    reason = (state.get("resolution") or {}).get("reason") or state.get("route_reason") or "needs human review"
    prio, queue = priority_and_queue(cls, mem, reason)
    summary = [f"Ticket {state['ticket_id']} | {cls.get('category')} | urgency={cls.get('urgency')} | "
               f"sentiment={cls.get('sentiment')} | complexity={cls.get('complexity')}",
               f"Customer message: {state.get('ticket_text', '')[:300]}",
               f"Why escalated: {reason}",
               f"Prior contacts: {mem.get('interaction_count', 0)} (open escalations: {mem.get('open_escalations', 0)})"]
    if state.get("kb_results"):
        summary.append("KB articles tried: " + ", ".join(f"{r['title']} ({r['confidence']:.2f})" for r in state["kb_results"]))
    if state.get("tool_usage"):
        summary.append("Tools used: " + ", ".join(f"{u['tool']}->{'ok' if u['ok'] else u['error_code']}" for u in state["tool_usage"][-5:]))
    text = "\n".join(summary)
    llm = get_llm()
    if llm is not None:
        try:  # optional: tighten the hand-off note
            text = llm.invoke([("system", "Write a 3-sentence hand-off note for a human support agent. Use only these facts."),
                               ("human", text)]).content or text
        except Exception as exc:
            log_event("llm_fallback", agent="escalation", ticket_id=state.get("ticket_id"), error=str(exc)[:200])
    with udahub_session() as db:
        db.add(TicketMessage(ticket_id=state["ticket_id"], role="system", agent="escalation", content=text))

    channel = mem.get("preferences", {}).get("contact_channel", "this conversation")
    name = first_name(mem.get("name"))
    empathy = "I'm sorry for the trouble. " if cls.get("sentiment") in ("negative", "angry") else ""
    prior = (state.get("draft_response") + "\n\n") if state.get("draft_response") else ""
    label = queue.replace("_", " ")
    label = label if label.endswith("team") else f"{label} team"
    reply = (f"{prior}{empathy}{'Thanks, ' + name + '. ' if name and not prior else ''}I've passed this to our {label} "
             f"as {prio} (reference {state['ticket_id']}). You'll hear back {SLA[prio]} via {channel}.")
    esc = {"priority": prio, "queue": queue, "reason": reason, "summary": text}
    return {"escalation": esc, "draft_response": reply,
            "resolution": {**(state.get("resolution") or {}), "status": "escalate", "reason": reason},
            "decision_log": [decision(state, "escalation", "escalated", priority=prio, queue=queue, reason=reason)]}
