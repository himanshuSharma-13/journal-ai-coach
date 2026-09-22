from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_session
from app.models import EntryChunk, EntryTheme, JournalEntry, JournalEvent, User
from app.schemas import JournalEntryCreate, JournalEntryPage, JournalEntryRead, JournalEntryUpdate, ThemeRead
from app.security import get_current_user
from app.services import chunk_text, create_embeddings, suggest_themes

router = APIRouter(prefix="/api/v1/entries", tags=["entries"])

def serialize(entry: JournalEntry) -> JournalEntryRead:
    return JournalEntryRead(id=entry.id, content=entry.content, occurred_at=entry.occurred_at, source=entry.source, created_at=entry.created_at, updated_at=entry.updated_at, themes=[ThemeRead(theme=item.theme, confidence=item.confidence, source=item.source) for item in entry.themes])

async def owned_entry(entry_id: uuid.UUID, user: User, session: AsyncSession) -> JournalEntry:
    entry = await session.scalar(select(JournalEntry).options(selectinload(JournalEntry.themes)).where(JournalEntry.id == entry_id, JournalEntry.user_id == user.id))
    if not entry: raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@router.post("", response_model=JournalEntryRead, status_code=status.HTTP_201_CREATED)
async def create_entry(payload: JournalEntryCreate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> JournalEntryRead:
    entry = JournalEntry(user_id=user.id, content=payload.content, occurred_at=payload.occurred_at, source=payload.source)
    session.add(entry); await session.flush()
    session.add_all([EntryChunk(entry_id=entry.id, chunk_index=index, content=chunk) for index, chunk in enumerate(chunk_text(entry.content))])
    session.add(JournalEvent(user_id=user.id, event_type="entry.created", entity_id=entry.id, payload={"source": entry.source}))
    await session.commit()
    return await get_entry(entry.id, user, session)

@router.get("", response_model=JournalEntryPage)
async def list_entries(start: Optional[datetime] = None, end: Optional[datetime] = None, limit: int = Query(30, ge=1, le=100), offset: int = Query(0, ge=0), user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> JournalEntryPage:
    filters = [JournalEntry.user_id == user.id]
    if start: filters.append(JournalEntry.occurred_at >= start)
    if end: filters.append(JournalEntry.occurred_at <= end)
    total = await session.scalar(select(func.count()).select_from(JournalEntry).where(*filters))
    entries = (await session.scalars(select(JournalEntry).options(selectinload(JournalEntry.themes)).where(*filters).order_by(JournalEntry.occurred_at.desc()).offset(offset).limit(limit))).all()
    return JournalEntryPage(items=[serialize(entry) for entry in entries], total=total or 0)

@router.get("/{entry_id}", response_model=JournalEntryRead)
async def get_entry(entry_id: uuid.UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> JournalEntryRead:
    return serialize(await owned_entry(entry_id, user, session))

@router.patch("/{entry_id}", response_model=JournalEntryRead)
async def update_entry(entry_id: uuid.UUID, payload: JournalEntryUpdate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> JournalEntryRead:
    entry = await owned_entry(entry_id, user, session)
    if payload.content is not None:
        entry.content = payload.content
        await session.execute(delete(EntryChunk).where(EntryChunk.entry_id == entry.id))
        session.add_all([EntryChunk(entry_id=entry.id, chunk_index=index, content=chunk) for index, chunk in enumerate(chunk_text(entry.content))])
    if payload.occurred_at is not None: entry.occurred_at = payload.occurred_at
    session.add(JournalEvent(user_id=user.id, event_type="entry.updated", entity_id=entry.id, payload={}))
    await session.commit()
    return await get_entry(entry.id, user, session)

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(entry_id: uuid.UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Response:
    await session.delete(await owned_entry(entry_id, user, session)); await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/{entry_id}/suggest-themes", response_model=list[ThemeRead])
async def create_theme_suggestions(entry_id: uuid.UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> list[ThemeRead]:
    entry = await owned_entry(entry_id, user, session)
    await session.execute(delete(EntryTheme).where(EntryTheme.entry_id == entry.id, EntryTheme.source == "suggested"))
    suggestions = [EntryTheme(entry_id=entry.id, theme=theme, confidence=confidence) for theme, confidence in suggest_themes(entry.content)]
    session.add_all(suggestions); await session.commit()
    return [ThemeRead(theme=item.theme, confidence=item.confidence, source=item.source) for item in suggestions]

@router.post("/{entry_id}/embed")
async def embed_entry(entry_id: uuid.UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> dict:
    entry = await owned_entry(entry_id, user, session)
    chunks = (await session.scalars(select(EntryChunk).where(EntryChunk.entry_id == entry.id).order_by(EntryChunk.chunk_index))).all()
    embeddings = create_embeddings([chunk.content for chunk in chunks])
    if embeddings is None:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is required to create embeddings")
    for chunk, embedding in zip(chunks, embeddings):
        chunk.embedding = embedding
        chunk.embedding_model = "text-embedding-3-small"
    await session.commit()
    return {"indexed_chunks": len(chunks), "model": "text-embedding-3-small"}
