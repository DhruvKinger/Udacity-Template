"""Structured, searchable logging: one JSON object per line (JSONL)."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from agentic import config

logger = logging.getLogger("udahub")


def log_event(event: str, **fields) -> dict:
    """Append a structured event to logs/udahub.jsonl and mirror it to the python logger."""
    record = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), "event": event, **fields}
    path = config.log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")
    logger.info("%s %s", event, json.dumps(fields, default=str))
    return record


def search_logs(path=None, **filters) -> list[dict]:
    """Return log records whose fields equal all given filters, e.g. search_logs(event="route_decision", ticket_id=...)."""
    path = path or config.log_path()
    out = []
    try:
        with open(path) as f:
            for line in f:
                rec = json.loads(line)
                if all(rec.get(k) == v for k, v in filters.items()):
                    out.append(rec)
    except FileNotFoundError:
        pass
    return out
