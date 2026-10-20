"""Tiny SQLAlchemy helper: one cached engine per database file."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from data.models.cultpass import CultPassBase
from data.models.udahub import UdaHubBase

_ENGINES: dict[str, object] = {}


def get_engine(path: Path, base):
    key = f"{path}"
    if key not in _ENGINES:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        eng = create_engine(f"sqlite:///{path}", future=True)

        @event.listens_for(eng, "connect")
        def _fk(dbapi_conn, _):  # enforce foreign keys in SQLite
            dbapi_conn.execute("PRAGMA foreign_keys=ON")

        base.metadata.create_all(eng)
        _ENGINES[key] = eng
    return _ENGINES[key]


@contextmanager
def session_scope(path: Path, base):
    """Commit on success, roll back on error, always close."""
    session = Session(get_engine(path, base), expire_on_commit=False)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def cultpass_session():
    from agentic.config import cultpass_db_path
    return session_scope(cultpass_db_path(), CultPassBase)


def udahub_session():
    from agentic.config import udahub_db_path
    return session_scope(udahub_db_path(), UdaHubBase)


def dispose_all():
    for eng in _ENGINES.values():
        eng.dispose()
    _ENGINES.clear()
