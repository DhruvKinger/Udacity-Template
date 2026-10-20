import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture()
def env(tmp_path, monkeypatch):
    """Fresh, isolated databases + log file for every test (offline / rule-based mode)."""
    shutil.copytree(ROOT / "data", tmp_path / "data", ignore=shutil.ignore_patterns("*.db", "__pycache__"))
    monkeypatch.setenv("UDAHUB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("UDAHUB_LOG_PATH", str(tmp_path / "logs.jsonl"))
    monkeypatch.setenv("UDAHUB_OFFLINE", "1")
    from agentic.db import dispose_all
    from agentic.llm import reset_llm
    from data.setup_db import setup_core_db, setup_external_db
    dispose_all(); reset_llm()
    setup_external_db(); setup_core_db()
    yield tmp_path
    dispose_all(); reset_llm()


@pytest.fixture()
def app(env):
    from agentic.workflow import create_app
    return create_app(persistent=False)
