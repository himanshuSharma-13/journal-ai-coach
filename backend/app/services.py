from __future__ import annotations

import re
from typing import Optional

from openai import OpenAI

from app.config import get_settings
from app.models import JournalEntry, Theme


def chunk_text(content: str, size: int = 900) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", content.strip())
    chunks, current = [], ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip()
        if len(candidate) > size and current:
            chunks.append(current)
            current = sentence
        else:
            current = candidate
    return chunks or [content]


def suggest_themes(content: str) -> list[tuple[Theme, float]]:
    text = content.lower()
    keywords = {
        Theme.CAREER: ("work", "job", "career", "interview", "project"),
        Theme.CREATIVITY: ("create", "write", "music", "art", "design"),
        Theme.HEALTH: ("sleep", "gym", "health", "workout", "energy"),
        Theme.LEARNING: ("learn", "study", "course", "read", "practice"),
        Theme.MINDSET: ("feel", "anxious", "confident", "mindset", "stress"),
        Theme.RELATIONSHIPS: ("friend", "family", "partner", "relationship"),
    }
    return [(theme, 0.65) for theme, terms in keywords.items() if any(term in text for term in terms)]


def create_embeddings(chunks: list[str]) -> Optional[list[list[float]]]:
    settings = get_settings()
    if not settings.openai_api_key:
        return None
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.embeddings.create(model=settings.openai_embedding_model, input=chunks)
    return [item.embedding for item in response.data]


def generate_insight(question: str, entries: list[JournalEntry]) -> tuple[str, str, Optional[str]]:
    evidence = "\n\n".join(f"[{entry.occurred_at.date()}] {entry.content}" for entry in entries)
    settings = get_settings()
    if settings.openai_api_key:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.responses.create(
            model=settings.openai_insight_model,
            store=False,
            instructions=(
                "Answer only from the journal evidence. Be concise, reflective, and explicit when evidence is weak. "
                "Do not diagnose or invent events. End with 2-4 dated evidence references."
            ),
            input=f"Question: {question}\n\nJournal evidence:\n{evidence}",
        )
        return response.output_text, "openai", settings.openai_insight_model
    if not entries:
        return "There are no entries in this period yet, so I cannot identify a grounded pattern.", "local-fallback", None
    return (
        f"You recorded {len(entries)} entries in this period. A full AI reflection will be available after OPENAI_API_KEY is configured. "
        f"For now, review the dated excerpts below as the evidence for your question: {question}",
        "local-fallback",
        None,
    )
