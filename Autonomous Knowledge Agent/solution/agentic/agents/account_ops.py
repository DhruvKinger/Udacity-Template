"""Account-operations agent: performs actions on the customer's CultPass account through TOOLS.

Deliberately a deterministic, auditable state machine (no free-form LLM tool loop) because it can change
money/subscriptions: identify -> (choose reservation) -> confirm -> execute. The multi-step state lives in
`pending_action`, which the checkpointer keeps per thread (short-term memory)."""
from __future__ import annotations

import re

from agentic.agents.common import call_tool, decision, first_name, latest_user_text
from agentic.memory import link_identity

MUTATING = {"cancel_subscription", "request_refund", "cancel_reservation"}
YES = r"^\s*(yes|y|yeah|yep|sure|confirm(ed)?|go ahead|proceed|do it|ok(ay)?|please do)\b"
NO = r"^\s*(no|n|nope|don'?t|do not|stop|cancel that|never ?mind|abort)\b"


def _result(state, reply, status="resolved", pending=None, usage=None, extra=None, reason=None, outcome=None, **log):
    out = {"draft_response": reply, "pending_action": pending, "tool_usage": usage or [],
           "resolution": {"status": status, "resolved_by": "account_ops", "confidence": 1.0,
                          "reason": reason, "outcome": outcome or reason},
           "decision_log": [decision(state, "account_ops", f"status_{status}", reason=reason, **log)]}
    out.update(extra or {})
    return out


def account_ops_node(state):
    cls = state["classification"]
    pending = dict(state.get("pending_action") or {})
    action = pending.get("action") or cls.get("action")
    if not action or action == "none":
        action = "lookup_account"
    ent = cls.get("entities", {})
    text = latest_user_text(state)
    usage: list[dict] = []
    extra: dict = {}

    # ---------------- 1. identify the customer ----------------
    user = pending.get("user")
    if not user:
        ext = state.get("external_user_id")
        lookup_args = {"user_id": ext} if ext else ({"email": ent["email"]} if ent.get("email") else None)
        if lookup_args is None:
            pending.update(action=action, stage="need_identity", user=None)
            return _result(state, "I can help with that. To find your account, could you please share the email "
                                  "address you use for CultPass?", "awaiting_customer", pending,
                           reason="need identity", outcome="asked for email")
        res, u = call_tool(state, "account_ops", "lookup_account", **lookup_args)
        usage.append(u)
        if not res["ok"]:
            attempts = pending.get("identity_attempts", 0) + 1
            if attempts >= 2 or res["error"]["code"] not in ("NOT_FOUND", "VALIDATION"):
                return _result(state, "I couldn't verify your account, so I'm handing this to a teammate "
                                      "who can check it with you.", "escalate", None, usage,
                               reason=f"identity could not be verified ({res['error']['code']})")
            pending.update(action=action, stage="need_identity", identity_attempts=attempts, user=None)
            return _result(state, "I couldn't find an account with those details. Could you double-check the email "
                                  "address you use for CultPass?", "awaiting_customer", pending, usage,
                           reason="identity not found", outcome="asked for email again")
        user = res["data"]
        if not ext:  # email-only identification: link to core user so memory works from now on
            core_id = link_identity(state["account_id"], state["ticket_id"], user["user_id"], user["full_name"], user["email"])
            extra.update(external_user_id=user["user_id"], user_id=core_id)
        pending["user"] = user
    if user.get("is_blocked"):
        return _result(state, "Your account needs a manual review, so I'm passing this to a specialist.",
                       "escalate", None, usage, extra, reason="account is blocked")

    uid, name = user["user_id"], first_name(user["full_name"])
    more = [a for a in cls.get("actions", []) if a != action and a != "none"]
    tail = f"\n\nYou also asked about {more[0].replace('_', ' ')}; send me another message and I'll handle that next." if more else ""

    # ---------------- 2. confirmation step for mutating actions ----------------
    if pending.get("stage") == "awaiting_confirmation":
        if re.match(YES, text, re.I):
            pass  # fall through to execution below
        elif re.match(NO, text, re.I):
            return _result(state, f"No problem, {name}. I haven't changed anything on your account.", "resolved",
                           None, usage, extra, reason="customer declined", outcome=f"{action} declined by customer")
        else:
            return _result(state, "Just to be safe, please reply YES to confirm or NO to keep things as they are.",
                           "awaiting_customer", pending, usage, extra, reason="awaiting confirmation")
        confirmed = True
    else:
        confirmed = False

    # ---------------- 3. read-only actions ----------------
    if action in ("check_subscription", "lookup_account"):
        res, u = call_tool(state, "account_ops", "get_subscription_status", user_id=uid)
        usage.append(u)
        if not res["ok"]:
            return _result(state, f"{name}, I couldn't find a subscription on your account. "
                                  "I'm asking a teammate to take a look.", "escalate", None, usage, extra,
                           reason=f"subscription lookup failed ({res['error']['code']})")
        d = res["data"]
        return _result(state, f"Hi {name}, you're on the {d['tier'].replace('_', ' ').title()} plan "
                              f"(${d['monthly_price']:.2f}), status: {d['status']}. You have {d['credits_remaining']} of "
                              f"{d['monthly_quota']} monthly experience credits left.{tail}",
                       "resolved", None, usage, extra, outcome="reported subscription status", reason="read-only lookup")

    if action == "list_reservations":
        res, u = call_tool(state, "account_ops", "list_reservations", user_id=uid)
        usage.append(u)
        rows = (res.get("data") or {}).get("reservations", [])
        if not rows:
            msg = f"Hi {name}, you have no upcoming reservations."
        else:
            msg = f"Hi {name}, here are your upcoming reservations:\n" + "\n".join(
                f"- {r['reservation_id']}: {r['experience']} at {r['location']} on {r['event_date']}" for r in rows)
        return _result(state, msg + tail, "resolved", None, usage, extra, outcome="listed reservations", reason="read-only lookup")

    # ---------------- 4. mutating actions ----------------
    if action == "cancel_subscription":
        if not confirmed:
            res, u = call_tool(state, "account_ops", "get_subscription_status", user_id=uid)
            usage.append(u)
            if not res["ok"]:
                return _result(state, "I couldn't find a subscription to cancel on your account.", "resolved",
                               None, usage, extra, reason=res["error"]["code"], outcome="no subscription found")
            d = res["data"]
            if d["status"] == "cancelled":
                return _result(state, f"{name}, your subscription is already cancelled, so there is nothing more to do.",
                               "resolved", None, usage, extra, outcome="already cancelled", reason="already cancelled")
            pending.update(action=action, stage="awaiting_confirmation")
            return _result(state, f"{name}, you're on the {d['tier'].replace('_', ' ').title()} plan. Do you want me to cancel it? "
                                  "Reply YES to confirm.", "awaiting_customer", pending, usage, extra, reason="awaiting confirmation")
        res, u = call_tool(state, "account_ops", "cancel_subscription", user_id=uid, reason="customer request via support chat")
        usage.append(u)
        if res["ok"]:
            return _result(state, f"Done, {name}. Your subscription has been cancelled and you won't be charged again. "
                                  "Reservations you already made stay valid." + tail, "resolved", None, usage, extra,
                           outcome="subscription cancelled", reason="executed")
        return _result(state, "I wasn't able to cancel the subscription, so I'm asking a teammate to help.", "escalate",
                       None, usage, extra, reason=f"cancel_subscription failed ({res['error']['code']})")

    if action == "cancel_reservation":
        rid = pending.get("reservation_id") or ent.get("reservation_id")
        if not rid:
            res, u = call_tool(state, "account_ops", "list_reservations", user_id=uid)
            usage.append(u)
            rows = (res.get("data") or {}).get("reservations", [])
            by_title = [r for r in rows if r["experience"].lower() in text.lower()]
            if not rows:
                return _result(state, f"{name}, you have no active reservations to cancel.", "resolved", None, usage,
                               extra, outcome="no reservations", reason="nothing to cancel")
            if len(rows) == 1 or len(by_title) == 1:
                rid = (by_title or rows)[0]["reservation_id"]
            else:
                pending.update(action=action, stage="choose_reservation")
                listing = "\n".join(f"- {r['reservation_id']}: {r['experience']} ({r['event_date']})" for r in rows)
                return _result(state, f"Which reservation should I cancel?\n{listing}\nReply with the reservation ID.",
                               "awaiting_customer", pending, usage, extra, reason="need reservation id")
        if not confirmed:
            pending.update(action=action, stage="awaiting_confirmation", reservation_id=rid)
            return _result(state, f"I'll cancel reservation {rid}. If it starts in more than 24 hours your credit is "
                                  "returned. Reply YES to confirm.", "awaiting_customer", pending, usage, extra,
                           reason="awaiting confirmation")
        res, u = call_tool(state, "account_ops", "cancel_reservation", user_id=uid, reservation_id=rid)
        usage.append(u)
        if res["ok"]:
            d = res["data"]
            credit = "Your experience credit has been returned." if d["credit_returned"] else \
                "It was inside the 24-hour window, so the credit is not returned."
            return _result(state, f"Done, reservation {rid} ({d['experience']}) is cancelled. {credit}" + tail,
                           "resolved", None, usage, extra, outcome=f"reservation {rid} cancelled", reason="executed")
        if res["error"]["code"] in ("NOT_FOUND", "NOT_ALLOWED"):
            return _result(state, res["error"]["message"], "resolved", None, usage, extra,
                           outcome=res["error"]["message"], reason=res["error"]["code"])
        return _result(state, "I couldn't cancel that reservation, so I'm asking a teammate to help.", "escalate",
                       None, usage, extra, reason=f"cancel_reservation failed ({res['error']['code']})")

    if action == "request_refund":
        elig, u = call_tool(state, "account_ops", "check_refund_eligibility", user_id=uid)
        usage.append(u)
        code = (elig.get("error") or {}).get("code")
        if code == "REQUIRES_APPROVAL":
            res, u2 = call_tool(state, "account_ops", "process_refund", user_id=uid, reason="customer request via support chat")
            usage.append(u2)
            d = res["data"] or {}
            return _result(state, f"{name}, your payment of ${d.get('amount', 0):.2f} is above the amount I can refund "
                                  f"automatically. I've logged the request ({d.get('refund_id')}) and a billing "
                                  "specialist will review it.", "escalate", None, usage, extra,
                           reason=f"refund of ${d.get('amount', 0):.2f} needs specialist approval", outcome="refund pending approval")
        if code in ("NOT_ALLOWED", "NOT_FOUND"):
            return _result(state, f"I'm sorry, {name}: {elig['error']['message']} You can see the full policy in our "
                                  "Refund policy article.", "resolved", None, usage, extra,
                           outcome=f"refund denied by policy: {elig['error']['message']}", reason=code)
        if code:
            return _result(state, "I couldn't check your refund eligibility, so I'm asking a teammate to help.",
                           "escalate", None, usage, extra, reason=f"refund check failed ({code})")
        d = elig["data"]
        if not confirmed:
            pending.update(action=action, stage="awaiting_confirmation")
            return _result(state, f"{name}, your latest payment of ${d['amount']:.2f} (paid {d['paid_at']}) is eligible. "
                                  "Shall I refund it to your original payment method? Reply YES to confirm.",
                           "awaiting_customer", pending, usage, extra, reason="awaiting confirmation")
        res, u = call_tool(state, "account_ops", "process_refund", user_id=uid, reason="customer request via support chat")
        usage.append(u)
        if res["ok"]:
            r = res["data"]
            return _result(state, f"Done, {name}. I've refunded ${r['amount']:.2f} (ref {r['refund_id']}). It reaches your "
                                  "card in 5 to 10 business days." + tail, "resolved", None, usage, extra,
                           outcome=f"refund {r['refund_id']} processed", reason="executed")
        return _result(state, "The refund could not be processed automatically, so I'm asking a teammate to help.",
                       "escalate", None, usage, extra, reason=f"process_refund failed ({res['error']['code']})")

    return _result(state, "I'm not sure how to help with that on your account, so I'm asking a teammate.",
                   "escalate", None, usage, extra, reason=f"unsupported action {action}")
