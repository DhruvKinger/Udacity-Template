"""RAG retrieval over the Knowledge table.

How it works (also documented in agentic/design/architecture.md):
 1. Articles for the account are loaded from the core DB (`knowledge` table).
 2. Each article is turned into one text blob: title (x3) + tags (x2) + content, so a title
    match outweighs an incidental word in the body.
 3. A TF-IDF model (word uni+bi-grams, sublinear tf, English stop-words) is fitted once per
    knowledge-base version and cached.
 4. A query is vectorised the same way; cosine similarity against every article is the
    *retrieval score* in [0, 1]. It is discounted by *coverage* (share of the query's content terms
    that appear in the article): confidence = score * (0.5 + 0.5 * coverage).
 5. The resolver escalates when the top confidence is below `config.confidence_threshold()`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import func, select

from agentic.db import udahub_session
from data.models.udahub import Knowledge

_CACHE: dict[tuple, "KnowledgeRetriever"] = {}

# --- light-weight text normalisation (no extra dependencies) ----------------------
_PHRASES = {"money back": "refund", "log in": "login", "sign in": "login", "logged in": "login",
            "locked out": "login lock", "qr code": "qrcode", "credit card": "card"}
_SYNONYMS = {"book": "reserv", "membership": "subscription", "invoic": "invoice", "receipt": "invoice",
             "bill": "billing", "charg": "payment charg"}
_SUFFIXES = ("ations", "ation", "ings", "ing", "ed", "es", "s", "ly")


def _stem(word: str) -> str:
    for suf in _SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 4:
            word = word[: -len(suf)]
            break
    if word.endswith("e") and len(word) > 4:
        word = word[:-1]
    if len(word) > 4 and word[-1] == word[-2] and word[-1] in "lstnr":
        word = word[:-1]
    return _SYNONYMS.get(word, word)


def normalise(text: str) -> str:
    text = text.lower()
    for k, v in _PHRASES.items():
        text = text.replace(k, v)
    words = re.findall(r"[a-z]{2,}", text)
    return " ".join(_stem(w) for w in words if w not in ENGLISH_STOP_WORDS)


@dataclass
class Article:
    article_id: str
    title: str
    content: str
    tags: str
    category: str | None


class KnowledgeRetriever:
    def __init__(self, articles: list[Article]):
        self.articles = articles
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, preprocessor=normalise)
        blobs = [f"{a.title} " * 3 + f"{a.tags} " * 2 + a.content for a in articles]
        self.matrix = self.vectorizer.fit_transform(blobs) if articles else None

    def search(self, query: str, k: int = 3) -> list[dict]:
        if not self.articles or not query.strip():
            return []
        sims = cosine_similarity(self.vectorizer.transform([query]), self.matrix)[0]
        q_terms = set(normalise(query).split())
        ranked = sorted(zip(self.articles, sims), key=lambda p: p[1], reverse=True)[:k]
        out = []
        for a, s in ranked:
            if s <= 0:
                continue
            a_terms = set(normalise(f"{a.title} {a.tags} {a.content}").split())
            coverage = len(q_terms & a_terms) / len(q_terms) if q_terms else 0.0
            # confidence = similarity, discounted when the article lacks many of the query's terms
            out.append({"article_id": a.article_id, "title": a.title, "content": a.content, "category": a.category,
                        "score": round(float(s), 4), "coverage": round(coverage, 3),
                        "confidence": round(float(s) * (0.5 + 0.5 * coverage), 4)})
        return sorted(out, key=lambda r: r["confidence"], reverse=True)


def get_retriever(account_id: str) -> KnowledgeRetriever:
    from agentic.config import udahub_db_path
    with udahub_session() as db:
        count = db.scalar(select(func.count()).select_from(Knowledge).where(Knowledge.account_id == account_id))
        key = (str(udahub_db_path()), account_id, count)
        if key not in _CACHE:
            rows = db.scalars(select(Knowledge).where(Knowledge.account_id == account_id)).all()
            _CACHE[key] = KnowledgeRetriever([Article(r.article_id, r.title, r.content, r.tags, r.category) for r in rows])
        return _CACHE[key]


def search_knowledge(account_id: str, query: str, k: int = 3) -> dict:
    """Tool-style entry point returning the same envelope as the DB tools."""
    if not query or not query.strip():
        return {"ok": False, "data": None, "error": {"code": "VALIDATION", "message": "Empty query."}}
    results = get_retriever(account_id).search(query, k)
    return {"ok": True, "data": {"results": results, "top_score": results[0]["confidence"] if results else 0.0}, "error": None}


def best_sentences(article_content: str, query: str, n: int = 3) -> list[str]:
    """Extractive answer helper: the n article sentences most similar to the query (original order)."""
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", article_content) if s.strip()]
    if len(sents) <= n:
        return sents
    vec = TfidfVectorizer(preprocessor=normalise).fit(sents + [query])
    sims = cosine_similarity(vec.transform([query]), vec.transform(sents))[0]
    top = sorted(sorted(range(len(sents)), key=lambda i: sims[i], reverse=True)[:n])
    return [sents[i] for i in top]
