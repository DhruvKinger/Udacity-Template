import pytest

from agentic.agents.classifier import rule_classify
from agentic.agents.supervisor import decide_route
from agentic.tools.kb_search import search_knowledge
from agentic import config


@pytest.mark.parametrize("query,title_part", [
    ("how do I cancel my subscription", "cancel your subscription"),
    ("I forgot my password and can't log in", "password"),
    ("my QR code won't scan", "QR code"),
    ("how do I pause my membership", "Pause"),
    ("where is my invoice", "invoice"),
    ("my card was declined", "declined"),
])
def test_relevant_article_is_retrieved_above_threshold(env, query, title_part):
    top = search_knowledge("cultpass", query)["data"]["results"][0]
    assert title_part.lower() in top["title"].lower()
    assert top["confidence"] >= config.confidence_threshold()


@pytest.mark.parametrize("query", ["what's the weather like in Paris", "how do I fix my car engine",
                                   "can I book a table at a restaurant", "tell me a joke"])
def test_off_topic_is_below_threshold(env, query):
    res = search_knowledge("cultpass", query)["data"]
    assert res["top_score"] < config.confidence_threshold()


def test_classifier_rules():
    assert rule_classify("How do I cancel my subscription?")["intent"] == "question"
    c = rule_classify("Please cancel my subscription")
    assert (c["intent"], c["action"], c["category"]) == ("account_action", "cancel_subscription", "subscription")
    assert rule_classify("I want a refund")["action"] == "request_refund"
    assert rule_classify("What is your refund policy?")["intent"] == "question"
    assert rule_classify("hello")["intent"] == "smalltalk"
    assert rule_classify("I was hacked, urgent!")["security_risk"] and rule_classify("I will sue you")["legal_risk"]
    assert rule_classify("Cancel reservation R1001 please")["action"] == "cancel_reservation"


def test_routing_decisions_use_content_and_metadata():
    q = {"intent": "question", "category": "billing", "urgency": "medium", "sentiment": "neutral"}
    assert decide_route(q, {}, None)[0] == "resolver"
    assert decide_route({**q, "intent": "account_action", "action": "request_refund"}, {}, None)[0] == "account_ops"
    assert decide_route({**q, "security_risk": True}, {}, None)[0] == "escalation"
    assert decide_route({**q, "legal_risk": True}, {}, None)[0] == "escalation"
    assert decide_route({**q, "human_requested": True}, {}, None)[0] == "escalation"
    # metadata / history: frustrated repeat contact, stale high-urgency ticket
    assert decide_route({**q, "sentiment": "angry"}, {"open_escalations": 1}, None)[0] == "escalation"
    assert decide_route({**q, "urgency": "high", "ticket_age_hours": 72}, {}, None)[0] == "escalation"
    assert decide_route(q, {}, {"action": "cancel_subscription"})[0] == "account_ops"
