"""LLM client: turns a question + retrieved context into a grounded answer with OpenAI."""

from typing import Dict, List

from openai_utils import get_openai_client

# The persona and the grounding rules for the model.
SYSTEM_PROMPT = """You are a NASA mission expert and archivist. You answer questions about the \
Apollo 11, Apollo 13 and Space Shuttle Challenger (STS-51L) missions using official NASA mission \
transcripts and technical documents.

Rules you must follow:
1. Ground every statement in the "Context" block of the user's message. Do not add facts, dates, \
numbers or quotes that are not supported by that context, even if you remember them from elsewhere. This applies especially to numbers, times and dates: state one only if it appears in a source, and cite only a source that actually contains the statement. When you quote a time, keep its time zone exactly as written in the source (for example CDT versus EDT) and do not add qualifiers the source does not contain.
2. If the context does not contain enough information, say so plainly (for example: "The retrieved \
archive excerpts do not contain enough information to answer this") and mention what is missing. \
Never guess or speculate. If only part of the question is covered, answer that part and state \
which part is not covered.
3. Cite your sources inline using the labels from the context, such as [Source 1] or \
[Source 2, Apollo 13], and name the mission when it matters. If sources disagree, point it out.
4. Keep missions separate: never attribute something that happened on one mission to another.
5. Radio transcripts use call signs such as CDR (Commander), CMP (Command Module Pilot), LMP (Lunar \
Module Pilot) and CC (Capsule Communicator, Mission Control). Explain them briefly when they help.
6. Use earlier turns of the conversation only to understand follow-up questions (for example what \
"it" or "that mission" refers to). Facts must still come from the current context.
7. Be clear, accurate and concise. Use short paragraphs or a short list when it helps. Treat the \
loss of the Challenger crew with appropriate respect."""

# Only the most recent messages are sent so that each request stays focused and affordable.
MAX_HISTORY_MESSAGES = 8
MAX_HISTORY_CHARS_PER_MESSAGE = 1200

NO_CONTEXT_NOTE = "No relevant excerpts were retrieved from the NASA archives for this question."


def build_messages(user_message: str, context: str,
                   conversation_history: List[Dict]) -> List[Dict[str, str]]:
    """Assemble the chat messages: system prompt, recent history, then context + question."""
    # System prompt
    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Chat history: keep role + content of the most recent turns only
    history = []
    for turn in conversation_history or []:
        role = turn.get("role")
        content = turn.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            history.append({"role": role, "content": content.strip()[:MAX_HISTORY_CHARS_PER_MESSAGE]})
    messages.extend(history[-MAX_HISTORY_MESSAGES:])

    # Context for *this* question only (earlier retrievals are not repeated)
    context_block = context.strip() if context and context.strip() else NO_CONTEXT_NOTE
    messages.append({
        "role": "user",
        "content": f"Context:\n{context_block}\n\nQuestion: {user_message.strip()}"
    })
    return messages


def generate_response(openai_key: str, user_message: str, context: str,
                     conversation_history: List[Dict], model: str = "gpt-3.5-turbo") -> str:
    """Generate response using OpenAI with context

    Args:
        openai_key: OpenAI API key
        user_message: The user's current question
        context: Formatted context from ``rag_client.format_context`` (may be empty)
        conversation_history: Earlier turns as ``[{"role": ..., "content": ...}, ...]``
        model: Chat model to use

    Returns:
        The model's answer as text.
    """
    if not user_message or not user_message.strip():
        raise ValueError("The question must not be empty.")

    messages = build_messages(user_message, context, conversation_history)

    # Create OpenAI client (handles Vocareum keys / custom endpoints)
    client = get_openai_client(openai_key)

    # Send request to OpenAI (a low temperature keeps the answer close to the context)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=700,
    )

    # Return response
    answer = response.choices[0].message.content
    if not answer or not answer.strip():
        return "I could not generate an answer. Please try rephrasing your question."
    return answer.strip()


EXPANSION_PROMPT = """You help search an archive of NASA mission documents: radio transcripts between \
astronauts and Mission Control, public-affairs commentary and technical reports about Apollo 11, \
Apollo 13 and the Space Shuttle Challenger (STS-51L).

Rewrite the user's question as one short passage (at most 60 words) that contains the specific \
words, names, equipment, call signs and phrases that would appear in the archive passages that \
answer it. Do not answer the question and do not add explanations. Output only the passage."""


def expand_query(openai_key: str, question: str, conversation_history: List[Dict] = None,
                 model: str = "gpt-3.5-turbo") -> str:
    """Rewrite a question into archive-style search terms to improve retrieval.

    Vague questions such as "What problems did Apollo 13 encounter?" do not look like the passages
    that answer them. The returned text is embedded together with the question so the search also
    matches the technical wording of the archive. Never raises: returns "" when it cannot expand.
    """
    try:
        if not question or not question.strip():
            return ""
        messages = [{"role": "system", "content": EXPANSION_PROMPT}]
        # the last turns help with follow-ups such as "and who was the commander?"
        for turn in (conversation_history or [])[-4:]:
            if turn.get("role") in ("user", "assistant") and isinstance(turn.get("content"), str):
                messages.append({"role": turn["role"], "content": turn["content"][:400]})
        messages.append({"role": "user", "content": question.strip()})
        response = get_openai_client(openai_key).chat.completions.create(
            model=model, messages=messages, temperature=0, max_tokens=120
        )
        return (response.choices[0].message.content or "").strip()
    except Exception:
        return ""
