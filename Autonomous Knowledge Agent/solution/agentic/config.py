"""Central configuration. Every path is resolved relative to this `solution/` folder
(nothing outside it is ever referenced) and is re-read at call time so tests can
redirect storage with environment variables."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]  # .../solution
load_dotenv(ROOT / ".env")

ACCOUNT_ID = "cultpass"

# --- business rules shared by tools, agents and the knowledge base -------------
REFUND_WINDOW_DAYS = 14
REFUND_AUTO_APPROVE_LIMIT = 50.00  # USD; above this a human must approve
MIN_COVERAGE = 0.4  # share of the question's terms the top article must contain


def data_dir() -> Path:
    return Path(os.getenv("UDAHUB_DATA_DIR", ROOT / "data"))


def cultpass_db_path() -> Path:
    return Path(os.getenv("CULTPASS_DB_PATH", data_dir() / "external" / "cultpass.db"))


def udahub_db_path() -> Path:
    return Path(os.getenv("UDAHUB_DB_PATH", data_dir() / "core" / "udahub.db"))


def checkpoint_db_path() -> Path:
    return Path(os.getenv("UDAHUB_CHECKPOINT_DB_PATH", data_dir() / "core" / "checkpoints.db"))


def log_path() -> Path:
    return Path(os.getenv("UDAHUB_LOG_PATH", ROOT / "logs" / "udahub.jsonl"))


def confidence_threshold() -> float:
    return float(os.getenv("UDAHUB_CONFIDENCE_THRESHOLD", "0.17"))


def offline_mode() -> bool:
    return os.getenv("UDAHUB_OFFLINE", "0") == "1" or not os.getenv("OPENAI_API_KEY")
