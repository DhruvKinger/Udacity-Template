"""LangGraph orchestration (Supervisor pattern), built from scratch with StateGraph - no prebuilt agents.

START -> intake -> load_memory -> classifier -> supervisor --+--> resolver -----+--> finalize -> END
                                                             +--> account_ops --+        ^
                                                             +--> escalation ------------+
(resolver / account_ops fall through to escalation when they cannot finish the job)
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from agentic import config
from agentic.agents.account_ops import account_ops_node
from agentic.agents.classifier import classifier_node
from agentic.agents.escalation import escalation_node
from agentic.agents.intake import intake_node
from agentic.agents.memory_agent import finalize_node, load_memory_node
from agentic.agents.resolver import resolver_node
from agentic.agents.supervisor import route_after_specialist, route_after_supervisor, supervisor_node
from agentic.state import UdaState


def build_graph(checkpointer=None):
    g = StateGraph(UdaState)
    g.add_node("intake", intake_node)
    g.add_node("load_memory", load_memory_node)
    g.add_node("classifier", classifier_node)
    g.add_node("supervisor", supervisor_node)
    g.add_node("resolver", resolver_node)
    g.add_node("account_ops", account_ops_node)
    g.add_node("escalation", escalation_node)
    g.add_node("finalize", finalize_node)

    g.add_edge(START, "intake")
    g.add_edge("intake", "load_memory")
    g.add_edge("load_memory", "classifier")
    g.add_edge("classifier", "supervisor")
    g.add_conditional_edges("supervisor", route_after_supervisor,
                            {"resolver": "resolver", "account_ops": "account_ops", "escalation": "escalation"})
    g.add_conditional_edges("resolver", route_after_specialist, {"escalation": "escalation", "finalize": "finalize"})
    g.add_conditional_edges("account_ops", route_after_specialist, {"escalation": "escalation", "finalize": "finalize"})
    g.add_edge("escalation", "finalize")
    g.add_edge("finalize", END)
    return g.compile(checkpointer=checkpointer)


def get_checkpointer(persistent: bool = True):
    """SQLite checkpointer keeps sessions across restarts; MemorySaver is the in-process alternative."""
    if not persistent:
        return MemorySaver()
    path = config.checkpoint_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return SqliteSaver(sqlite3.connect(str(path), check_same_thread=False))


def create_app(persistent: bool = True):
    return build_graph(get_checkpointer(persistent))


def run_ticket(app, text: str, thread_id: str | None = None, *, external_user_id: str | None = None,
               channel: str = "chat", created_at: str | None = None, account_id: str = config.ACCOUNT_ID) -> dict:
    """Send one customer message through the graph. Re-use `thread_id` to continue the same session."""
    thread_id = thread_id or f"thread-{uuid.uuid4().hex[:8]}"
    cfg = {"configurable": {"thread_id": thread_id}}
    payload = {"messages": [HumanMessage(content=text)], "thread_id": thread_id, "account_id": account_id,
               "channel": channel}
    existing = app.get_state(cfg).values
    if not existing:  # first turn of this session: ticket metadata comes from the caller
        if external_user_id:
            payload["external_user_id"] = external_user_id
        if created_at:
            payload["created_at"] = created_at
    out = app.invoke(payload, cfg)
    out["thread_id"] = thread_id
    return out


def inspect_thread(app, thread_id: str) -> dict:
    """Inspect a session: messages, tool usage, decisions, pending action (scoped by thread_id)."""
    v = app.get_state({"configurable": {"thread_id": thread_id}}).values
    return {"messages": [(m.type, m.content) for m in v.get("messages", [])], "tool_usage": v.get("tool_usage", []),
            "decision_log": v.get("decision_log", []), "pending_action": v.get("pending_action"),
            "classification": v.get("classification"), "ticket_id": v.get("ticket_id"),
            "resolution": v.get("resolution")}
