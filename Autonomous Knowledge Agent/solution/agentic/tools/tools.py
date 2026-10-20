"""LangChain tool wrappers (what agents invoke) around the DB service layer + KB search.
Each tool returns the structured envelope from `cultpass_db` / `kb_search`."""
from __future__ import annotations

from langchain_core.tools import tool

from agentic.tools import cultpass_db as db
from agentic.tools import kb_search


@tool
def lookup_account(email: str = "", user_id: str = "") -> dict:
    """Look up a CultPass customer by email or user_id and return profile + subscription summary."""
    return db.lookup_account(email=email or None, user_id=user_id or None)


@tool
def get_subscription_status(user_id: str) -> dict:
    """Get the customer's current subscription tier, status and remaining experience credits."""
    return db.get_subscription_status(user_id)


@tool
def cancel_subscription(user_id: str, reason: str = "") -> dict:
    """Cancel the customer's subscription. Only call after the customer explicitly confirmed."""
    return db.cancel_subscription(user_id, reason)


@tool
def list_reservations(user_id: str) -> dict:
    """List the customer's confirmed experience reservations."""
    return db.list_reservations(user_id)


@tool
def cancel_reservation(user_id: str, reservation_id: str) -> dict:
    """Cancel one reservation. Only call after the customer explicitly confirmed."""
    return db.cancel_reservation(user_id, reservation_id)


@tool
def process_refund(user_id: str, reason: str = "") -> dict:
    """Refund the latest payment per policy (14 days, auto-approve up to $50). Needs customer confirmation."""
    return db.process_refund(user_id, reason)


@tool
def check_refund_eligibility(user_id: str) -> dict:
    """Read-only: check whether the customer's latest payment can be refunded under policy."""
    return db.check_refund_eligibility(user_id)


@tool
def search_knowledge_base(account_id: str, query: str) -> dict:
    """Retrieve the most relevant support articles for a customer question (with similarity scores)."""
    return kb_search.search_knowledge(account_id, query)


TOOLS = {t.name: t for t in (lookup_account, get_subscription_status, cancel_subscription,
                             list_reservations, cancel_reservation, process_refund, check_refund_eligibility,
                             search_knowledge_base)}
