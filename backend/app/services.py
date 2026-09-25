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
    settings = get_settings()
    if not entries:
        return "There are no entries in this period yet, so I cannot identify a grounded pattern.", "local-fallback", None
    evidence = "\n\n".join(f"[{entry.occurred_at.date()}] {entry.content}" for entry in entries)
    if settings.groq_api_key:
        client = OpenAI(api_key=settings.groq_api_key, base_url="https://api.groq.com/openai/v1")
        response = client.responses.create(
            model=settings.groq_insight_model,
            instructions=(
                "Answer the question using only the journal evidence. Write concise Markdown: begin with a direct "
                "1-2 sentence answer, then a '### What I noticed' section with up to three short bullets, "
                "and a '### Next step' section with one practical suggestion about the activities described, "
                "only if the evidence supports one. "
                "Put an evidence date next to each observation. If evidence is weak, say so clearly. "
                "Do not invent events, diagnoses, scores, percentages, or trends. Do not make tables, "
                "ASCII charts, or code blocks. If asked for a graph, explain that these free-form entries "
                "are not numerical data and give a short dated qualitative timeline instead. "
                "Do not suggest changing the journal format or adding ratings, scores, hours, counts, "
                "or other tracking fields."
            ),
            input=f"Question: {question}\n\nJournal evidence:\n{evidence}",
        )
        return response.output_text, "groq", settings.groq_insight_model
    return (
        f"You recorded {len(entries)} entries in this period. A full AI reflection will be available after GROQ_API_KEY is configured. "
        f"For now, review the dated excerpts below as the evidence for your question: {question}",
        "local-fallback",
        None,
    )
