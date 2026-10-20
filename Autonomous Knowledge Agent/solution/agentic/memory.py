"""Long-term memory + identity helpers backed by the core DB.

* Short-term memory  = LangGraph checkpointer, keyed by thread_id (see workflow.py).
* Long-term memory   = `customer_memory` table: resolved issues + preferences per customer,
                       recalled with TF-IDF similarity (same normaliser as the KB retriever).
* Conversation log   = `tickets` / `ticket_messages` tables (persistent history).
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select

from agentic.db import udahub_session
from agentic.tools.kb_search import normalise
from data.models.udahub import CustomerMemory, Ticket, TicketMessage, User

PREFERENCE_PATTERNS = [
    ("response_style", "concise", r"\b(keep it (short|brief)|be (brief|concise)|short answers?|brief answers?|tl;?dr)\b"),
    ("response_style", "detailed", r"\b(more detail|detailed (answer|explanation)|step[- ]by[- ]step|explain in detail)\b"),
    ("contact_channel", "email", r"\b(reply|respond|contact|write|get back to) (me )?(by|via|through|on) email\b|\bemail me\b"),
    ("contact_channel", "sms", r"\b(text me|sms me|contact me (by|via) (sms|text))\b"),
]


def extract_preferences(text: str) -> dict:
    prefs = {}
    for key, value, pattern in PREFERENCE_PATTERNS:
        if re.search(pattern, text, re.I):
            prefs[key] = value
    m = re.search(r"\bcall me ([A-Z][a-z]{1,15})\b", text)
    if m:
        prefs["preferred_name"] = m.group(1)
    return prefs


def get_or_create_user(account_id: str, external_user_id: str | None) -> dict | None:
    if not external_user_id:
        return None
    with udahub_session() as db:
        u = db.scalars(select(User).where(User.account_id == account_id,
                                          User.external_user_id == external_user_id)).first()
        if not u:
            u = User(account_id=account_id, external_user_id=external_user_id)
            db.add(u)
            db.flush()
        return {"user_id": u.user_id, "name": u.user_name, "email": u.email}


def link_identity(account_id: str, ticket_id: str, external_user_id: str, name: str, email: str) -> str:
    """Attach a verified CultPass identity to the core user and to the open ticket."""
    with udahub_session() as db:
        u = db.scalars(select(User).where(User.account_id == account_id,
                                          User.external_user_id == external_user_id)).first()
        if not u:
            u = User(account_id=account_id, external_user_id=external_user_id)
            db.add(u)
        u.user_name, u.email = name, email
        db.flush()
        t = db.get(Ticket, ticket_id)
        if t:
            t.user_id = u.user_id
        return u.user_id


def save_preferences(account_id: str, user_id: str, prefs: dict, ticket_id: str | None = None) -> None:
    with udahub_session() as db:
        for key, value in prefs.items():
            row = db.scalars(select(CustomerMemory).where(
                CustomerMemory.user_id == user_id, CustomerMemory.kind == "preference",
                CustomerMemory.key == key)).first()
            if row:
                row.content, row.created_at = value, datetime.utcnow()
            else:
                db.add(CustomerMemory(account_id=account_id, user_id=user_id, kind="preference", key=key,
                                      content=value, ticket_id=ticket_id))


def save_resolved_issue(account_id: str, user_id: str, ticket_id: str, summary: str, tags: list[str]) -> None:
    with udahub_session() as db:
        db.add(CustomerMemory(account_id=account_id, user_id=user_id, kind="resolved_issue",
                              content=summary, tags=tags, ticket_id=ticket_id))


def load_memory(account_id: str, user_id: str | None, query: str, current_ticket_id: str | None = None,
                top_k: int = 2, min_similarity: float = 0.2) -> dict:
    """Everything the agents may use to personalise: profile, preferences, similar past issues, history stats."""
    empty = {"known_customer": False, "name": None, "email": None, "preferences": {}, "past_issues": [],
             "interaction_count": 0, "open_escalations": 0, "recent_issues": []}
    if not user_id:
        return empty
    with udahub_session() as db:
        user = db.get(User, user_id)
        if not user:
            return empty
        mems = db.scalars(select(CustomerMemory).where(CustomerMemory.user_id == user_id)).all()
        prefs = {m.key: m.content for m in mems if m.kind == "preference"}
        issues = [m for m in mems if m.kind == "resolved_issue" and m.ticket_id != current_ticket_id]
        tickets = db.scalars(select(Ticket).where(Ticket.user_id == user_id)).all()
        others = [t for t in tickets if t.ticket_id != current_ticket_id]
        recent = datetime.utcnow() - timedelta(days=30)
        open_esc = sum(1 for t in others if t.status == "escalated" and t.updated_at >= recent)
        past = []
        if issues and query.strip():
            vec = TfidfVectorizer(preprocessor=normalise).fit([m.content for m in issues] + [query])
            sims = cosine_similarity(vec.transform([query]), vec.transform([m.content for m in issues]))[0]
            for m, s in sorted(zip(issues, sims), key=lambda p: p[1], reverse=True)[:top_k]:
                if s >= min_similarity:
                    past.append({"summary": m.content, "similarity": round(float(s), 3),
                                 "date": m.created_at.date().isoformat(), "ticket_id": m.ticket_id})
        return {"known_customer": True, "name": user.user_name, "email": user.email, "preferences": prefs,
                "past_issues": past, "recent_issues": [
                    {"summary": m.content, "date": m.created_at.date().isoformat()}
                    for m in sorted(issues, key=lambda m: m.created_at, reverse=True)[:10]],
                "interaction_count": len(others), "open_escalations": open_esc}


def customer_history(user_id: str, limit: int = 20) -> list[dict]:
    """Persistent conversation history across all of the customer's tickets (oldest first)."""
    with udahub_session() as db:
        rows = db.execute(select(TicketMessage, Ticket).join(Ticket, Ticket.ticket_id == TicketMessage.ticket_id)
                          .where(Ticket.user_id == user_id).order_by(TicketMessage.created_at.desc())
                          .limit(limit)).all()
        return [{"ticket_id": t.ticket_id, "role": m.role, "content": m.content, "at": m.created_at.isoformat()}
                for m, t in reversed(rows)]
