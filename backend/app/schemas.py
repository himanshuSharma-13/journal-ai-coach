from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import Theme


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class JournalEntryCreate(BaseModel):
    content: str = Field(min_length=20, max_length=20000)
    occurred_at: datetime
    source: str = Field(default="manual", min_length=1, max_length=40)

    @field_validator("occurred_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at must include a timezone offset")
        return value


class JournalEntryUpdate(BaseModel):
    content: Optional[str] = Field(default=None, min_length=20, max_length=20000)
    occurred_at: Optional[datetime] = None


class ThemeRead(BaseModel):
    theme: Theme
    confidence: float
    source: str


class JournalEntryRead(JournalEntryCreate):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    themes: list[ThemeRead] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class JournalEntryPage(BaseModel):
    items: list[JournalEntryRead]
    total: int


class InsightRequest(BaseModel):
    question: str = Field(min_length=5, max_length=1000)
    period_start: datetime
    period_end: datetime


class InsightEvidence(BaseModel):
    entry_id: uuid.UUID
    excerpt: str = Field(max_length=500)
    occurred_at: datetime


class InsightRead(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    period_start: datetime
    period_end: datetime
    evidence: list[InsightEvidence]
    provider: str
    model: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    status: str
    service: str
