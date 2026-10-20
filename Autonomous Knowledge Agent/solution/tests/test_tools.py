from agentic.tools import cultpass_db as db
from agentic.tools.tools import TOOLS


def test_lookup_ok_and_not_found_and_validation(env):
    ok = db.lookup_account(email="alice@example.com")
    assert ok["ok"] and ok["data"]["user_id"] == "u_alice" and ok["data"]["subscription"]["tier"] == "premium"
    assert db.lookup_account(email="nobody@example.com")["error"]["code"] == "NOT_FOUND"
    assert db.lookup_account(email="not-an-email")["error"]["code"] == "VALIDATION"
    assert db.lookup_account()["error"]["code"] == "VALIDATION"


def test_subscription_status_and_cancel(env):
    s = db.get_subscription_status("u_alice")
    assert s["ok"] and 0 <= s["data"]["credits_remaining"] <= 6
    assert db.cancel_subscription("u_alice")["ok"]
    assert db.cancel_subscription("u_alice")["error"]["code"] == "NOT_ALLOWED"  # idempotency guard
    assert db.cancel_subscription("u_erin")["error"]["code"] == "BLOCKED"
    assert db.cancel_subscription("")["error"]["code"] == "VALIDATION"


def test_reservations(env):
    rows = db.list_reservations("u_alice")["data"]["reservations"]
    assert {r["reservation_id"] for r in rows} == {"R1001", "R1002"}
    assert db.cancel_reservation("u_bob", "R1001")["error"]["code"] == "NOT_FOUND"  # someone else's booking
    assert db.cancel_reservation("u_alice", "R1001")["ok"]
    assert db.cancel_reservation("u_alice", "R1001")["error"]["code"] == "NOT_ALLOWED"


def test_refund_policy(env):
    assert db.process_refund("u_alice")["data"]["status"] == "processed"          # <= $50, in window
    assert db.process_refund("u_alice")["error"]["code"] == "NOT_ALLOWED"          # already refunded
    assert db.process_refund("u_bob")["error"]["code"] == "NOT_ALLOWED"            # 40 days old
    r = db.process_refund("u_dev")                                                  # $299.99
    assert r["error"]["code"] == "REQUIRES_APPROVAL" and r["data"]["status"] == "pending_approval"
    assert db.check_refund_eligibility("u_grace")["ok"]


def test_langchain_tools_return_structured_envelopes(env):
    out = TOOLS["lookup_account"].invoke({"email": "bob@example.com"})
    assert set(out) == {"ok", "data", "error"} and out["data"]["full_name"] == "Bob Smith"
    kb = TOOLS["search_knowledge_base"].invoke({"account_id": "cultpass", "query": "cancel subscription"})
    assert kb["ok"] and kb["data"]["results"]
