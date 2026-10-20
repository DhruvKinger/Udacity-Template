"""Create and seed the two databases. Used by notebooks 01 and 02 and by the tests."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from agentic import config
from agentic.db import dispose_all, session_scope
from data.models.cultpass import (CultPassBase, CultPassUser, Experience, Payment,
                                  Reservation, Subscription)
from data.models.udahub import Account, Knowledge, UdaHubBase, User
from sqlalchemy import func, select


def _read_jsonl(path: Path) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _reset(path: Path):
    dispose_all()
    for suffix in ("", "-journal", "-wal", "-shm"):
        p = Path(f"{path}{suffix}")
        if p.exists():
            p.unlink()


def setup_external_db(db_path: Path | None = None, src_dir: Path | None = None, reset: bool = True) -> dict:
    """Notebook 01: build the CultPass (customer-side) database."""
    db_path = Path(db_path or config.cultpass_db_path())
    src = Path(src_dir or config.data_dir() / "external")
    if reset:
        _reset(db_path)
    now = datetime.utcnow()
    ago = lambda d: None if d is None else now - timedelta(days=d)
    with session_scope(db_path, CultPassBase) as s:
        for r in _read_jsonl(src / "cultpass_users.jsonl"):
            s.add(CultPassUser(user_id=r["user_id"], full_name=r["full_name"], email=r["email"],
                               is_blocked=r["is_blocked"], created_at=ago(r["created_days_ago"])))
        s.flush()
        for r in _read_jsonl(src / "cultpass_subscriptions.jsonl"):
            s.add(Subscription(subscription_id=r["subscription_id"], user_id=r["user_id"], tier=r["tier"],
                               status=r["status"], monthly_price=r["monthly_price"], monthly_quota=r["monthly_quota"],
                               started_at=ago(r["started_days_ago"]), ended_at=ago(r["ended_days_ago"])))
        for r in _read_jsonl(src / "cultpass_experiences.jsonl"):
            s.add(Experience(experience_id=r["experience_id"], title=r["title"], description=r["description"],
                             location=r["location"], event_date=now + timedelta(days=r["days_ahead"]),
                             slots_available=r["slots_available"]))
        s.flush()
        for r in _read_jsonl(src / "cultpass_reservations.jsonl"):
            s.add(Reservation(reservation_id=r["reservation_id"], user_id=r["user_id"], experience_id=r["experience_id"],
                              status=r["status"], created_at=ago(r["created_days_ago"])))
        for r in _read_jsonl(src / "cultpass_payments.jsonl"):
            s.add(Payment(payment_id=r["payment_id"], user_id=r["user_id"], subscription_id=r["subscription_id"],
                          amount=r["amount"], status=r["status"], paid_at=ago(r["paid_days_ago"])))
    return external_counts(db_path)


def external_counts(db_path: Path | None = None) -> dict:
    db_path = Path(db_path or config.cultpass_db_path())
    with session_scope(db_path, CultPassBase) as s:
        return {m.__tablename__: s.scalar(select(func.count()).select_from(m))
                for m in (CultPassUser, Subscription, Experience, Reservation, Payment)}


def setup_core_db(db_path: Path | None = None, articles_path: Path | None = None,
                  external_db_path: Path | None = None, reset: bool = True) -> dict:
    """Notebook 02: build the UDA-Hub core database, load KB articles and mirror CultPass users."""
    db_path = Path(db_path or config.udahub_db_path())
    articles_path = Path(articles_path or config.data_dir() / "core" / "cultpass_articles.jsonl")
    if reset:
        _reset(db_path)
    with session_scope(db_path, UdaHubBase) as s:
        s.add(Account(account_id=config.ACCOUNT_ID, account_name="CultPass"))
        s.flush()
        for a in _read_jsonl(articles_path):
            s.add(Knowledge(article_id=a["article_id"], account_id=config.ACCOUNT_ID, title=a["title"],
                            content=a["content"], tags=a.get("tags", ""), category=a.get("category")))
    ext = Path(external_db_path or config.cultpass_db_path())
    if ext.exists():
        with session_scope(ext, CultPassBase) as es, session_scope(db_path, UdaHubBase) as s:
            for u in es.scalars(select(CultPassUser)):
                s.add(User(user_id=f"usr-{u.user_id}", account_id=config.ACCOUNT_ID,
                           external_user_id=u.user_id, user_name=u.full_name, email=u.email))
    return core_counts(db_path)


def core_counts(db_path: Path | None = None) -> dict:
    from data.models.udahub import (CustomerMemory, Ticket, TicketMessage, TicketMetadata)
    db_path = Path(db_path or config.udahub_db_path())
    with session_scope(db_path, UdaHubBase) as s:
        return {m.__tablename__: s.scalar(select(func.count()).select_from(m))
                for m in (Account, User, Ticket, TicketMetadata, TicketMessage, Knowledge, CustomerMemory)}
