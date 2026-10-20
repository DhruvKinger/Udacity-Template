"""Shared LangGraph state. Checkpointed per thread_id => short-term (session) memory."""
from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class UdaState(TypedDict, total=False):
    # ---- conversation (persists across turns of one thread) ----
    messages: Annotated[list[BaseMessage], add_messages]
    tool_usage: Annotated[list[dict], operator.add]      # every tool call, cumulative
    decision_log: Annotated[list[dict], operator.add]    # every agent decision, cumulative
    pending_action: dict | None                           # multi-step account operation in progress
    # ---- ticket / identity ----
    thread_id: str
    ticket_id: str
    account_id: str
    user_id: str | None                                   # UDA-Hub core user
    external_user_id: str | None                          # id in the customer's system (CultPass)
    channel: str
    created_at: str                                       # ISO time the ticket was opened
    # ---- per-turn working fields (reset by intake each turn) ----
    ticket_text: str
    classification: dict
    memory_context: dict
    route: str | None
    route_reason: str | None
    kb_results: list[dict]
    resolution: dict
    escalation: dict
    draft_response: str
    final_response: str
