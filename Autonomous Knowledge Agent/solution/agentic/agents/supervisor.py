"""Supervisor agent: decides which specialist handles the ticket (and records why)."""
from __future__ import annotations

from agentic.agents.common import decision


def decide_route(cls: dict, memory: dict, pending: dict | None) -> tuple[str, str]:
    """Pure function => easy to unit test. Order matters: safety first, then continuity, then fit."""
    if pending:
        return "account_ops", "continuing a multi-step account operation"
    if cls.get("security_risk"):
        return "escalation", "security risk (possible fraud/unauthorised access)"
    if cls.get("legal_risk"):
        return "escalation", "legal/chargeback threat"
    if cls.get("human_requested"):
        return "escalation", "customer asked for a human"
    if cls.get("urgency") == "critical":
        return "escalation", "critical urgency"
    if cls.get("sentiment") in ("angry", "negative") and memory.get("open_escalations", 0) >= 1:
        return "escalation", "frustrated repeat contact with an unresolved earlier escalation"
    if cls.get("urgency") == "high" and (cls.get("ticket_age_hours") or 0) > 48:
        return "escalation", "high-urgency ticket open for more than 48h"
    if cls.get("intent") == "account_action":
        return "account_ops", f"customer wants an account action ({cls.get('action')})"
    return "resolver", f"{cls.get('intent')} about {cls.get('category')} -> knowledge-based resolution"


def supervisor_node(state):
    route, reason = decide_route(state["classification"], state.get("memory_context", {}), state.get("pending_action"))
    return {"route": route, "route_reason": reason,
            "decision_log": [decision(state, "supervisor", "route", route=route, reason=reason,
                                      complexity=state["classification"].get("complexity"))]}


def route_after_supervisor(state) -> str:
    return state["route"]


def route_after_specialist(state) -> str:
    return "escalation" if state.get("resolution", {}).get("status") == "escalate" else "finalize"
