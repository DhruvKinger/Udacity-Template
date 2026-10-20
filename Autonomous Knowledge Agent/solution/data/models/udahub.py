"""CORE database: the UDA-Hub application itself (multi-tenant)."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class UdaHubBase(DeclarativeBase):
    pass


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


class Account(UdaHubBase):
    __tablename__ = "accounts"
    account_id: Mapped[str] = mapped_column(String, primary_key=True)
    account_name: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class User(UdaHubBase):
    __tablename__ = "users"
    user_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("usr"))
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.account_id"), index=True)
    external_user_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    user_name: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Ticket(UdaHubBase):
    __tablename__ = "tickets"
    ticket_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("tkt"))
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.account_id"), index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id"), nullable=True, index=True)
    channel: Mapped[str] = mapped_column(String, default="chat")
    status: Mapped[str] = mapped_column(String, default="open")  # open|awaiting_customer|resolved|escalated
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TicketMetadata(UdaHubBase):
    __tablename__ = "ticket_metadata"
    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.ticket_id"), primary_key=True)
    status: Mapped[str] = mapped_column(String, default="open")
    main_issue_type: Mapped[str | None] = mapped_column(String, nullable=True)
    intent: Mapped[str | None] = mapped_column(String, nullable=True)
    urgency: Mapped[str | None] = mapped_column(String, nullable=True)
    sentiment: Mapped[str | None] = mapped_column(String, nullable=True)
    complexity: Mapped[str | None] = mapped_column(String, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    routed_to: Mapped[str | None] = mapped_column(String, nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    escalation_queue: Mapped[str | None] = mapped_column(String, nullable=True)
    escalation_priority: Mapped[str | None] = mapped_column(String, nullable=True)
    escalation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TicketMessage(UdaHubBase):
    __tablename__ = "ticket_messages"
    message_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("msg"))
    ticket_id: Mapped[str] = mapped_column(ForeignKey("tickets.ticket_id"), index=True)
    role: Mapped[str] = mapped_column(String)  # user | assistant | system
    agent: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Knowledge(UdaHubBase):
    __tablename__ = "knowledge"
    article_id: Mapped[str] = mapped_column(String, primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.account_id"), index=True)
    title: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    tags: Mapped[str] = mapped_column(String, default="")
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CustomerMemory(UdaHubBase):
    """Long-term memory: resolved issues + stated preferences, per customer."""
    __tablename__ = "customer_memory"
    memory_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("mem"))
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.account_id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), index=True)
    kind: Mapped[str] = mapped_column(String)  # resolved_issue | preference
    key: Mapped[str | None] = mapped_column(String, nullable=True)  # preference name
    content: Mapped[str] = mapped_column(Text)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    ticket_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
