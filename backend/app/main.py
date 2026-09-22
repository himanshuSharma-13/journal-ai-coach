from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine
from app.models import Base
from app.routers import auth, entries, insights
from app.schemas import HealthResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


settings = get_settings()
app = FastAPI(title="Journal AI Coach API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)
app.include_router(entries.router)
app.include_router(auth.router)
app.include_router(insights.router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="journal-ai-coach-api")
