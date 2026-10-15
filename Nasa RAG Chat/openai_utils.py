"""Small shared helpers for creating OpenAI clients consistently.

Every module that talks to OpenAI (embedding pipeline, RAG client, LLM client and
the RAGAS evaluator) goes through these helpers so that API-key handling and the
endpoint (``base_url``) are configured in exactly one place.

Endpoint resolution order:
1. ``OPENAI_BASE_URL`` environment variable (e.g. a proxy or a local test server)
2. Udacity/Vocareum keys (start with ``voc``) -> ``https://openai.vocareum.com/v1``
3. ``None`` -> the standard OpenAI endpoint
"""

import os
from typing import Optional

from openai import OpenAI

VOCAREUM_BASE_URL = "https://openai.vocareum.com/v1"

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def resolve_base_url(api_key: Optional[str]) -> Optional[str]:
    """Return the base URL to use for the given API key (``None`` = OpenAI default)."""
    env_url = os.getenv("OPENAI_BASE_URL")
    if env_url:
        return env_url
    if api_key and api_key.startswith("voc"):
        return VOCAREUM_BASE_URL
    return None


def get_openai_client(api_key: str) -> OpenAI:
    """Create an OpenAI client for ``api_key`` using the correct endpoint."""
    if not api_key or not api_key.strip():
        raise ValueError("An OpenAI API key is required.")
    return OpenAI(api_key=api_key.strip(), base_url=resolve_base_url(api_key))


def get_api_key_from_env() -> Optional[str]:
    """Look for an API key in the environment variables used by this project.

    ``CHROMA_OPENAI_API_KEY`` is exported by the chat app for the key typed into its
    sidebar, so it takes priority over a general ``OPENAI_API_KEY``.
    """
    return os.getenv("CHROMA_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
