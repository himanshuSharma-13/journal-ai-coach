from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import JournalEntry
from app.schemas import JournalEntryCreate, JournalEntryPage, JournalEntryRead

router = APIRouter(prefix="/api/v1/entries", tags=["entries"])


@router.post("", response_model=JournalEntryRead, status_code=status.HTTP_201_CREATED)
async def create_entry(
    payload: JournalEntryCreate,
    session: AsyncSession = Depends(get_session),
) -> JournalEntry:
    entry = JournalEntry(
        content=payload.content,
        occurred_at=payload.occurred_at,
        source=payload.source,
    )
    session.add(entry)
    await session.commit()

    created = await session.scalar(
        select(JournalEntry).where(JournalEntry.id == entry.id)
    )
    return created


@router.get("", response_model=JournalEntryPage)
async def list_entries(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> JournalEntryPage:
    filters = []
    if start:
        filters.append(JournalEntry.occurred_at >= start)
    if end:
        filters.append(JournalEntry.occurred_at <= end)
    total = await session.scalar(select(func.count()).select_from(JournalEntry).where(*filters))
    entries = await session.scalars(
        select(JournalEntry).where(*filters)
        .order_by(JournalEntry.occurred_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return JournalEntryPage(items=list(entries), total=total or 0)
