"""End-to-end scenarios through the compiled LangGraph app (offline mode)."""
from datetime import datetime, timedelta

from sqlalchemy import select

from agentic.db import udahub_session
from agentic.llm import set_llm
from agentic.logging_utils import search_logs
from agentic.memory import customer_history
from agentic.workflow import inspect_thread, run_ticket
from data.models.udahub import CustomerMemory, Ticket, TicketMessage, TicketMetadata


def test_kb_resolution(app):
    out = run_ticket(app, "How do I reset my password?")
    assert out["route"] == "resolver" and out["resolution"]["status"] == "resolved"
    assert "Forgot Password" in out["final_response"]            # answer comes from the KB article
    assert out["resolution"]["article_ids"] == ["kb-009"]
    with udahub_session() as db:
        assert db.get(Ticket, out["ticket_id"]).status == "resolved"


def test_escalation_when_no_article(app):
    out = run_ticket(app, "What's the weather like in Paris?")
    assert out["resolution"]["status"] == "escalate" and out["escalation"]["queue"] == "general_support"
    with udahub_session() as db:
        assert db.get(TicketMetadata, out["ticket_id"]).escalation_reason.startswith("no relevant")
        assert db.get(Ticket, out["ticket_id"]).status == "escalated"
        assert any(m.role == "system" for m in db.scalars(select(TicketMessage)))   # hand-off note


def test_security_goes_straight_to_escalation(app):
    out = run_ticket(app, "Someone hacked my account and made unauthorized charges!")
    assert out["route"] == "escalation" and out["escalation"]["priority"] == "P1"
    assert out["escalation"]["queue"] == "trust_and_safety"


def test_old_high_urgency_ticket_is_escalated_by_metadata(app):
    old = (datetime.utcnow() - timedelta(hours=72)).isoformat()
    out = run_ticket(app, "I need help with my invoice today, it's urgent", created_at=old)
    assert out["route"] == "escalation" and "48h" in out["route_reason"]


def test_multi_turn_cancel_subscription_with_short_term_memory(app):
    t1 = run_ticket(app, "Please cancel my subscription")
    tid = t1["thread_id"]
    assert t1["resolution"]["status"] == "awaiting_customer" and "email" in t1["final_response"].lower()
    t2 = run_ticket(app, "my email is bob@example.com", tid)
    assert "YES" in t2["final_response"] and t2["pending_action"]["stage"] == "awaiting_confirmation"
    t3 = run_ticket(app, "yes", tid)
    assert t3["resolution"]["status"] == "resolved" and "cancelled" in t3["final_response"]
    assert t3["ticket_id"] == t1["ticket_id"]                      # same ticket / same session
    info = inspect_thread(app, tid)
    assert [u["tool"] for u in info["tool_usage"]] == ["lookup_account", "get_subscription_status", "cancel_subscription"]
    assert len(info["messages"]) == 6 and info["pending_action"] is None
    from agentic.tools import cultpass_db
    assert cultpass_db.get_subscription_status("u_bob")["data"]["status"] == "cancelled"


def test_declining_confirmation_changes_nothing(app):
    tid = run_ticket(app, "Please cancel my subscription", external_user_id="u_alice")["thread_id"]
    out = run_ticket(app, "no", tid)
    from agentic.tools import cultpass_db
    assert "haven't changed" in out["final_response"]
    assert cultpass_db.get_subscription_status("u_alice")["data"]["status"] == "active"


def test_refund_success_denied_and_escalated(app):
    ok = run_ticket(app, "I want a refund", external_user_id="u_grace")
    out = run_ticket(app, "yes", ok["thread_id"])
    assert out["resolution"]["status"] == "resolved" and "refunded $29.99" in out["final_response"]
    denied = run_ticket(app, "I want a refund", external_user_id="u_bob")
    assert denied["resolution"]["status"] == "resolved" and "older than" in denied["final_response"]
    big = run_ticket(app, "I want a refund", external_user_id="u_dev")
    assert big["resolution"]["status"] == "escalate" and big["escalation"]["queue"] == "billing_team"


def test_error_handling_bad_identity_and_blocked_account(app):
    t = run_ticket(app, "Please cancel my subscription")["thread_id"]
    assert "double-check" in run_ticket(app, "nobody@example.com", t)["final_response"]
    assert run_ticket(app, "still nobody@example.com", t)["resolution"]["status"] == "escalate"
    blocked = run_ticket(app, "Please cancel my subscription", external_user_id="u_erin")
    assert blocked["resolution"]["status"] == "escalate" and "blocked" in blocked["resolution"]["reason"]


def test_cancel_reservation_requires_choice_and_blocks_foreign_ids(app):
    t = run_ticket(app, "Please cancel my reservation", external_user_id="u_alice")
    assert "R1001" in t["final_response"] and "R1002" in t["final_response"]
    t = run_ticket(app, "R1002", t["thread_id"])
    assert "YES" in t["final_response"]
    assert "cancelled" in run_ticket(app, "yes", t["thread_id"])["final_response"]
    other = run_ticket(app, "cancel reservation R1003 please", external_user_id="u_alice")
    run_ticket(app, "yes", other["thread_id"])
    from agentic.tools import cultpass_db
    assert cultpass_db.list_reservations("u_bob")["data"]["reservations"][0]["status"] == "confirmed"


def test_long_term_memory_across_sessions(app):
    first = run_ticket(app, "How do I reset my password? Please keep it short.", external_user_id="u_alice")
    with udahub_session() as db:
        kinds = {(m.kind, m.key) for m in db.scalars(select(CustomerMemory))}
    assert ("preference", "response_style") in kinds and any(k == "resolved_issue" for k, _ in kinds)
    second = run_ticket(app, "I forgot my password again, how do I reset it?", external_user_id="u_alice")  # NEW thread
    assert second["thread_id"] != first["thread_id"]
    assert second["memory_context"]["past_issues"] and second["memory_context"]["preferences"]["response_style"] == "concise"
    assert "contacted us about something similar" in second["final_response"]
    assert second["final_response"].startswith("Hi Alice")
    assert len(customer_history(second["user_id"])) >= 4        # persisted history across tickets


def test_structured_searchable_logs(app):
    out = run_ticket(app, "Please cancel my subscription", external_user_id="u_alice")
    tid = out["ticket_id"]
    routes = search_logs(event="agent_decision", ticket_id=tid, agent="supervisor")
    assert routes and routes[0]["route"] == "account_ops" and routes[0]["reason"]
    assert search_logs(event="tool_call", ticket_id=tid, tool="lookup_account")
    assert search_logs(event="ticket_outcome", ticket_id=tid)[0]["status"] == "awaiting_customer"


def test_llm_path_with_stub_model(app):
    """Exercise the LLM branches (classifier + resolver) with a stub that mimics structured output."""
    from agentic.agents.classifier import TicketClassification
    from agentic.agents.resolver import ResolverOutput

    class Stub:
        def __init__(self, schema=None): self.schema = schema
        def with_structured_output(self, schema): return Stub(schema)
        def invoke(self, _):
            if self.schema is TicketClassification:
                return TicketClassification(category="technical", intent="question")
            return ResolverOutput(can_answer=True, answer="Update the app, then reinstall it.", confidence=0.9,
                                  used_article_ids=["kb-013"])
    set_llm(Stub())
    out = run_ticket(app, "my app keeps crashing when I open it")
    assert out["resolution"]["status"] == "resolved" and "Update the app" in out["final_response"]

    class CannotAnswer(Stub):
        def invoke(self, _):
            if self.schema is TicketClassification:
                return TicketClassification(category="technical", intent="question")
            return ResolverOutput(can_answer=False, answer="", confidence=0.2)
        def with_structured_output(self, schema): return CannotAnswer(schema)
    set_llm(CannotAnswer())
    assert run_ticket(app, "my app keeps crashing when I open it")["resolution"]["status"] == "escalate"

    class Broken(Stub):
        def with_structured_output(self, schema): raise RuntimeError("API down")
    set_llm(Broken())                                   # falls back to rules instead of crashing
    assert run_ticket(app, "How do I reset my password?")["resolution"]["status"] == "resolved"
    assert search_logs(event="llm_fallback")


def test_partial_keyword_match_is_not_answered(app):
    out = run_ticket(app, "Do you sell gift cards for my cat?")       # shares only the word 'card' with a KB article
    assert out["resolution"]["status"] == "escalate" and "covers only" in out["resolution"]["reason"]


def test_memory_mentions_same_article_issue(app):
    run_ticket(app, "How do I reset my password?", external_user_id="u_grace")
    again = run_ticket(app, "I forgot my password again, what do I do?", external_user_id="u_grace")
    assert "contacted us about something similar" in again["final_response"]
