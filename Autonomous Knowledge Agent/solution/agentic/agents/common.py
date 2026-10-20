"""Helpers shared by the agents."""
from __future__ import annotations

from datetime import datetime

from langchain_core.messages import HumanMessage

from agentic.logging_utils import log_event
from agentic.tools.tools import TOOLS


def latest_user_text(state) -> str:
    for m in reversed(state.get("messages", [])):
        if isinstance(m, HumanMessage):
            return m.content if isinstance(m.content, str) else str(m.content)
    return ""


def previous_user_text(state) -> str:
    seen = 0
    for m in reversed(state.get("messages", [])):
        if isinstance(m, HumanMessage):
            seen += 1
            if seen == 2:
                return m.content
    return ""


def decision(state, agent: str, name: str, **details) -> dict:
    """Create a decision-log entry AND write it to the structured log file."""
    entry = {"agent": agent, "decision": name, "ts": datetime.utcnow().isoformat(timespec="seconds"), **details}
    log_event("agent_decision", ticket_id=state.get("ticket_id"), thread_id=state.get("thread_id"),
              agent=agent, decision=name, **details)
    return entry


def call_tool(state, agent: str, tool_name: str, **args) -> tuple[dict, dict]:
    """Invoke a LangChain tool, returning (result_envelope, usage_entry). Never raises."""
    try:
        result = TOOLS[tool_name].invoke(args)
    except Exception as exc:  # tool/schema failure must not crash the graph
        result = {"ok": False, "data": None, "error": {"code": "TOOL_ERROR", "message": str(exc)}}
    err = (result or {}).get("error") or {}
    usage = {"tool": tool_name, "args": {k: v for k, v in args.items()}, "ok": result.get("ok"),
             "error_code": err.get("code"), "agent": agent, "ts": datetime.utcnow().isoformat(timespec="seconds")}
    log_event("tool_call", ticket_id=state.get("ticket_id"), thread_id=state.get("thread_id"), agent=agent,
              tool=tool_name, args=args, ok=result.get("ok"), error_code=err.get("code"))
    return result, usage


def first_name(full: str | None) -> str | None:
    return full.split()[0] if full else None
