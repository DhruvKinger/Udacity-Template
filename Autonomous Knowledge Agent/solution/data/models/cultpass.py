"""EXTERNAL database: the customer's own system (CultPass)."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class CultPassBase(DeclarativeBase):
    pass


class CultPassUser(CultPassBase):
    __tablename__ = "cultpass_users"
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    full_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime)


class Subscription(CultPassBase):
    __tablename__ = "subscriptions"
    subscription_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("cultpass_users.user_id"), index=True)
    tier: Mapped[str] = mapped_column(String)  # basic | premium | premium_annual
    status: Mapped[str] = mapped_column(String)  # active | cancelled | paused | expired
    monthly_price: Mapped[float] = mapped_column(Float)
    monthly_quota: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(DateTime)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Experience(CultPassBase):
    __tablename__ = "experiences"
    experience_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String)
    event_date: Mapped[datetime] = mapped_column(DateTime)
    slots_available: Mapped[int] = mapped_column(Integer)


class Reservation(CultPassBase):
    __tablename__ = "reservations"
    reservation_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("cultpass_users.user_id"), index=True)
    experience_id: Mapped[str] = mapped_column(ForeignKey("experiences.experience_id"))
    status: Mapped[str] = mapped_column(String)  # confirmed | cancelled | attended
    created_at: Mapped[datetime] = mapped_column(DateTime)


class Payment(CultPassBase):
    __tablename__ = "payments"
    payment_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("cultpass_users.user_id"), index=True)
    subscription_id: Mapped[str] = mapped_column(ForeignKey("subscriptions.subscription_id"))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String, default="USD")
    status: Mapped[str] = mapped_column(String)  # paid | refunded
    paid_at: Mapped[datetime] = mapped_column(DateTime)


class Refund(CultPassBase):
    __tablename__ = "refunds"
    refund_id: Mapped[str] = mapped_column(String, primary_key=True)
    payment_id: Mapped[str] = mapped_column(ForeignKey("payments.payment_id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("cultpass_users.user_id"))
    amount: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String)  # processed | pending_approval
    created_at: Mapped[datetime] = mapped_column(DateTime)
