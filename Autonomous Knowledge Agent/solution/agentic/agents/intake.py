"""Intake agent: opens (or continues) the ticket, persists the incoming message, resets per-turn fields."""
from __future__ import annotations

from datetime import datetime

from agentic import config
from agentic.agents.common import decision, latest_user_text
from agentic.db import udahub_session
from agentic.memory import get_or_create_user
from data.models.udahub import Ticket, TicketMessage, TicketMetadata


def intake_node(state):
    account_id = state.get("account_id") or config.ACCOUNT_ID
    text = latest_user_text(state)
    ext = state.get("external_user_id")
    user = get_or_create_user(account_id, ext) if ext else None
    user_id = user["user_id"] if user else state.get("user_id")
    channel = state.get("channel") or "chat"
    ticket_id = state.get("ticket_id")
    created_at = state.get("created_at")
    with udahub_session() as db:
        if not ticket_id:
            created = datetime.fromisoformat(created_at) if created_at else datetime.utcnow()
            t = Ticket(account_id=account_id, user_id=user_id, channel=channel, status="open",
                       created_at=created, updated_at=datetime.utcnow())
            db.add(t)
            db.flush()
            db.add(TicketMetadata(ticket_id=t.ticket_id, status="open"))
            ticket_id, created_at = t.ticket_id, created.isoformat()
        db.add(TicketMessage(ticket_id=ticket_id, role="user", content=text))
    entry = decision({"ticket_id": ticket_id, "thread_id": state.get("thread_id")}, "intake", "ticket_received",
                     channel=channel, user_known=bool(user_id), text_preview=text[:80])
    return {"account_id": account_id, "ticket_id": ticket_id, "user_id": user_id, "channel": channel,
            "created_at": created_at, "ticket_text": text,
            # per-turn reset
            "route": None, "route_reason": None, "kb_results": [], "resolution": {}, "escalation": {},
            "draft_response": "", "final_response": "", "decision_log": [entry]}
