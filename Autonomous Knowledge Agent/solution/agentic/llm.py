"""LLM access. Returns None in offline mode (no OPENAI_API_KEY or UDAHUB_OFFLINE=1); every agent has a
deterministic rule-based path for that case. `set_llm` lets tests inject a stub."""
from __future__ import annotations

import os

from agentic import config

_OVERRIDE = {"llm": None, "set": False}


def set_llm(llm) -> None:
    _OVERRIDE.update(llm=llm, set=True)


def reset_llm() -> None:
    _OVERRIDE.update(llm=None, set=False)


def get_llm():
    if _OVERRIDE["set"]:
        return _OVERRIDE["llm"]
    if config.offline_mode():
        return None
    from langchain_openai import ChatOpenAI
    kwargs = {"model": os.getenv("UDAHUB_MODEL", "gpt-4o-mini"), "temperature": 0}
    if os.getenv("OPENAI_BASE_URL"):
        kwargs["base_url"] = os.getenv("OPENAI_BASE_URL")
    return ChatOpenAI(**kwargs)
