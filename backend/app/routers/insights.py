from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import EntryChunk, Insight, JournalEntry, User
from app.schemas import InsightRead, InsightRequest
from app.security import get_current_user
from app.services import create_embeddings, generate_insight

router = APIRouter(prefix="/api/v1/insights", tags=["insights"])


@router.post("", response_model=InsightRead)
async def create_insight(payload: InsightRequest, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> Insight:
    filters = (JournalEntry.user_id == user.id, JournalEntry.occurred_at >= payload.period_start, JournalEntry.occurred_at <= payload.period_end)
    query_embedding = create_embeddings([payload.question])
    if query_embedding:
        chunks = (await session.scalars(select(EntryChunk).join(JournalEntry).where(*filters, EntryChunk.embedding.is_not(None)).order_by(EntryChunk.embedding.cosine_distance(query_embedding[0])).limit(12))).all()
        entry_ids = list(dict.fromkeys(chunk.entry_id for chunk in chunks))
        entries = (await session.scalars(select(JournalEntry).where(JournalEntry.id.in_(entry_ids)))).all() if entry_ids else []
    else:
        entries = (await session.scalars(select(JournalEntry).where(*filters).order_by(JournalEntry.occurred_at.desc()).limit(30))).all()
    answer, provider, model = generate_insight(payload.question, entries)
    evidence = [{"entry_id": str(entry.id), "occurred_at": entry.occurred_at.isoformat(), "excerpt": entry.content[:500]} for entry in entries[:5]]
    insight = Insight(user_id=user.id, question=payload.question, answer=answer, period_start=payload.period_start, period_end=payload.period_end, evidence=evidence, provider=provider, model=model)
    session.add(insight); await session.commit(); await session.refresh(insight)
    return insight


@router.get("", response_model=list[InsightRead])
async def list_insights(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> list[Insight]:
    return (await session.scalars(select(Insight).where(Insight.user_id == user.id).order_by(Insight.created_at.desc()).limit(20))).all()
