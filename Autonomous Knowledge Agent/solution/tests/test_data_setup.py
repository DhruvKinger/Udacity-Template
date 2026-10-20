from sqlalchemy import inspect, select

from agentic.db import get_engine, udahub_session
from agentic import config
from data.models.udahub import Knowledge, UdaHubBase
from data.setup_db import core_counts, external_counts


def test_required_tables_exist(env):
    names = set(inspect(get_engine(config.udahub_db_path(), UdaHubBase)).get_table_names())
    # Account, User, Ticket, TicketMetadata, TicketMessage, Knowledge (+ our customer_memory)
    assert {"accounts", "users", "tickets", "ticket_metadata", "ticket_messages", "knowledge"} <= names


def test_knowledge_base_has_14_plus_diverse_articles(env):
    assert core_counts()["knowledge"] >= 14  # 4 provided + at least 10 new
    with udahub_session() as db:
        cats = {a.category for a in db.scalars(select(Knowledge))}
    assert len(cats) >= 5 and {"technical", "billing", "account"} <= cats


def test_external_data_retrievable(env):
    c = external_counts()
    assert c["cultpass_users"] >= 5 and c["subscriptions"] >= 5
