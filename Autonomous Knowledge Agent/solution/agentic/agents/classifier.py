"""Classifier agent: category, intent/action, urgency, sentiment, complexity + risk flags + entities.
LLM structured output when available; deterministic rules otherwise (rules also act as a safety net for flags)."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from agentic.agents.common import decision, latest_user_text
from agentic.llm import get_llm
from agentic.logging_utils import log_event

CATEGORIES = ["billing", "subscription", "reservations", "account", "technical", "experiences", "general", "other"]
ACTIONS = ["none", "cancel_subscription", "request_refund", "cancel_reservation",
           "check_subscription", "list_reservations", "lookup_account"]
URGENCY = ["low", "medium", "high", "critical"]


class TicketClassification(BaseModel):
    category: Literal["billing", "subscription", "reservations", "account", "technical", "experiences", "general", "other"]
    intent: Literal["question", "account_action", "smalltalk", "unclear"] = Field(
        description="account_action = the customer wants something DONE on their account")
    action: Literal["none", "cancel_subscription", "request_refund", "cancel_reservation",
                    "check_subscription", "list_reservations", "lookup_account"] = "none"
    urgency: Literal["low", "medium", "high", "critical"] = "medium"
    sentiment: Literal["positive", "neutral", "negative", "angry"] = "neutral"
    complexity: Literal["simple", "moderate", "complex"] = "simple"
    legal_risk: bool = False
    security_risk: bool = False
    human_requested: bool = False


CATEGORY_KEYWORDS = {
    "billing": r"refund|charge|payment|invoice|receipt|price|pricing|billing|card|declined|cost|money",
    "subscription": r"subscription|subscribe|membership|\bplan\b|\bpause|renew|upgrade|downgrade",
    "reservations": r"reservation|reserve|\bbook|credits?|quota",
    "account": r"password|log ?in|email address|profile|delete (my )?account|\baccount\b|username|locked",
    "technical": r"\bapp\b|crash|\bbug\b|error|\bqr\b|scan|notification|loading|freez|\bslow|install|website",
    "experiences": r"experience|concert|workshop|\btour\b|venue|partner|museum|organi[sz]er",
}
ACTION_PATTERNS = [
    ("cancel_reservation", r"\bcancel\b.*\b(reservation|booking|experience)\b|\bR\d{4}\b.*\bcancel|\bcancel\b.*\bR\d{4}\b"),
    ("cancel_subscription", r"\bcancel\b.*\b(subscription|membership|plan)\b|\b(subscription|membership)\b.*\bcancel"),
    ("request_refund", r"\brefund|money back|reimburse"),
    ("list_reservations", r"\b(my|upcoming|show|list)\b.*\b(reservations|bookings)\b|what (have i|did i) (booked|reserved)|do i have any (reservations|bookings)"),
    ("check_subscription", r"\b(my|current)\b.*\b(subscription|plan|membership)\b(?!.*cancel)|credits? (left|remaining)|am i subscribed|how many (credits|experiences) (do i have|are left|left)"),
    ("lookup_account", r"look ?up my account|find my account|my account details"),
]
INFO_OVERRIDE = r"\b(how (do|can|to|does|would)|policy|is it possible|where (do|can|is)|what happens|steps)\b"
STRONG_IMPERATIVE = r"\b(please|i want to|i'd like to|i would like to|i need to|i wish to|can you|could you|would you)\b"
READ_ONLY_ACTIONS = {"list_reservations", "check_subscription", "lookup_account"}
SMALLTALK = r"^\s*(hi|hello|hey|good (morning|afternoon|evening)|thanks|thank you|thx|bye|ok|okay|cheers)\b[\s!.,]*(there|team|support)?[\s!.,]*$"
LEGAL = r"\b(lawyer|attorney|sue\b|suing|legal action|court|chargeback|lawsuit|consumer protection)\b"
SECURITY = r"\b(hacked|fraud|fraudulent|unauthori[sz]ed|stolen|identity theft|compromised|someone (else )?(logged|accessed))\b"
HUMAN = r"\b(human|real person|manager|supervisor|representative|speak to (an? )?(agent|someone)|talk to (an? )?(agent|someone))\b"
ANGRY = r"\b(furious|unacceptable|terrible|worst|ridiculous|angry|scam|outrageous|disgusting|useless)\b|!!"
NEGATIVE = r"\b(disappointed|frustrated|annoyed|not happy|upset|unhappy|still (not|no)|again)\b"
POSITIVE = r"\b(thanks|thank you|great|love|awesome|appreciate)\b"
HIGH = r"\b(urgent|asap|immediately|right now|today|emergency|locked out|can'?t access|cannot access|double charged|charged twice|tonight|deadline)\b"
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
RES_ID = re.compile(r"\bR\d{4}\b", re.I)


def extract_entities(text: str) -> dict:
    ent = {}
    if m := EMAIL.search(text):
        ent["email"] = m.group(0).lower().rstrip(".")
    if m := RES_ID.search(text):
        ent["reservation_id"] = m.group(0).upper()
    return ent


def rule_classify(text: str) -> dict:
    t = text.lower()
    words = len(text.split())
    scores = {c: len(re.findall(p, t)) for c, p in CATEGORY_KEYWORDS.items()}
    matched = [c for c, n in scores.items() if n]
    category = max(scores, key=scores.get) if matched else "other"
    actions = [a for a, p in ACTION_PATTERNS if re.search(p, text, re.I)]
    if any(a not in READ_ONLY_ACTIONS for a in actions):  # "cancel my subscription" is not also a status check
        actions = [a for a in actions if a not in READ_ONLY_ACTIONS]
    action = actions[0] if actions else "none"
    if action != "none" and action not in READ_ONLY_ACTIONS:
        if re.search(INFO_OVERRIDE, t) and not re.search(STRONG_IMPERATIVE, t):
            action = "none"
    if action != "none":
        category = {"cancel_subscription": "subscription", "request_refund": "billing",
                    "cancel_reservation": "reservations", "check_subscription": "subscription",
                    "list_reservations": "reservations", "lookup_account": "account"}[action]
    if re.match(SMALLTALK, t):
        intent, category = "smalltalk", "general"
    elif action != "none":
        intent = "account_action"
    elif words < 3 and not matched:
        intent = "unclear"
    else:
        intent = "question"
    legal, security = bool(re.search(LEGAL, t)), bool(re.search(SECURITY, t))
    urgency = "critical" if security else "high" if re.search(HIGH, t) else "medium"
    sentiment = "angry" if re.search(ANGRY, t) or legal else "negative" if re.search(NEGATIVE, t) \
        else "positive" if re.search(POSITIVE, t) else "neutral"
    complexity = "complex" if (len(matched) >= 3 or words > 80 or legal or security) \
        else "moderate" if (len(matched) == 2 or intent == "account_action") else "simple"
    return {"category": category, "intent": intent, "action": action, "actions": actions, "urgency": urgency,
            "sentiment": sentiment, "complexity": complexity, "legal_risk": legal, "security_risk": security,
            "human_requested": bool(re.search(HUMAN, t))}


def _bump(level: str) -> str:
    return URGENCY[min(URGENCY.index(level) + 1, 2)] if level in ("low", "medium") else level


def classifier_node(state):
    text = latest_user_text(state)
    pending = state.get("pending_action")
    if pending and state.get("classification"):
        # follow-up inside a multi-step operation: keep the original classification, refresh entities
        cls = {**state["classification"], "entities": {**state["classification"].get("entities", {}),
                                                       **extract_entities(text)}}
        return {"classification": cls, "decision_log": [decision(
            state, "classifier", "classification_reused", reason="pending_action", action=pending.get("action"))]}

    rules = rule_classify(text)
    cls, source = dict(rules), "rules"
    llm = get_llm()
    if llm is not None:
        try:
            prior = state.get("memory_context", {})
            out = llm.with_structured_output(TicketClassification).invoke([
                ("system", "You classify customer-support tickets for CultPass (a cultural-experiences subscription). "
                           "Use intent=account_action only when the customer wants something done on THEIR account "
                           "(cancel, refund, look up status); questions about how things work are intent=question."),
                ("human", f"Channel: {state.get('channel')}\nPrior contacts: {prior.get('interaction_count', 0)}\nTicket: {text}")])
            cls.update(out.model_dump())
            # rule-based safety net: risk flags can only be switched ON by rules, never off
            for flag in ("legal_risk", "security_risk", "human_requested"):
                cls[flag] = cls[flag] or rules[flag]
            source = "llm"
        except Exception as exc:
            log_event("llm_fallback", agent="classifier", ticket_id=state.get("ticket_id"), error=str(exc)[:200])
    # metadata-aware adjustment: old tickets get more urgent
    age_h = None
    if state.get("created_at"):
        age_h = (datetime.utcnow() - datetime.fromisoformat(state["created_at"])).total_seconds() / 3600
        if age_h > 24 and cls["urgency"] in ("low", "medium"):
            cls["urgency"] = _bump(cls["urgency"])
            cls["urgency_reason"] = f"ticket open {age_h:.0f}h"
    cls["ticket_age_hours"] = round(age_h, 1) if age_h is not None else None
    cls["entities"] = extract_entities(text)
    cls.setdefault("actions", [cls["action"]] if cls["action"] != "none" else [])
    return {"classification": cls, "decision_log": [decision(
        state, "classifier", "classified", source=source, category=cls["category"], intent=cls["intent"],
        action=cls["action"], urgency=cls["urgency"], sentiment=cls["sentiment"], complexity=cls["complexity"],
        flags=[f for f in ("legal_risk", "security_risk", "human_requested") if cls[f]])]}
