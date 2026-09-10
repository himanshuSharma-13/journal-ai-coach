from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

class JournalEntryCreate(BaseModel):
    """The Phase 0 contract for a user-authored journal entry."""

    content: str = Field(min_length=20, max_length=20000)
    occurred_at: datetime
    source: str = Field(default="manual", min_length=1, max_length=40)

    @field_validator("occurred_at")
    @classmethod
    def occurred_at_requires_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at must include a timezone offset")
        return value

class JournalEntryRead(JournalEntryCreate):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JournalEntryPage(BaseModel):
    items: list[JournalEntryRead]
    total: int


class HealthResponse(BaseModel):
    status: str
    service: str


class InsightEvidence(BaseModel):
    entry_id: uuid.UUID
    excerpt: str = Field(max_length=500)
    occurred_at: datetime


class ThemeInsightContract(BaseModel):
    """Reserved Phase 0 contract for the later RAG/analysis pipeline."""

    theme: str = Field(min_length=1, max_length=80)
    period_start: datetime
    period_end: datetime
    trend: str = Field(pattern="^(improving|steady|declining|unclear)$")
    confidence: float = Field(ge=0, le=1)
    summary: str
    wins: list[str]
    blockers: list[str]
    evidence: list[InsightEvidence]
