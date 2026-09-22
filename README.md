# Journal AI Coach

A general-purpose product for free-form journaling and long-term, user-requested AI reflection.

## Repository Layout

```text
frontend/                 Next.js + TypeScript client
backend/                  FastAPI + SQLAlchemy service
docs/                     Product design and API/data contracts
docker-compose.yml        Local Postgres infrastructure
```

## Product Capabilities

The first release is intentionally small:

- Write a free-form journal entry.
- Save the original entry permanently in Postgres.
- Browse the timeline and filter it by date.
- Create an account and keep journal data isolated per user.
- Edit or permanently delete entries and all derived data.
- Request a short evidence-backed insight for a date range.
- Generate optional theme suggestions without requiring themes during writing.
- Create retrieval-ready chunks and analytics events for future RAG and pipelines.

Themes, mood/energy tracking, habits, dashboards, and automatic AI summaries are deferred until they demonstrate a clear product benefit. See [the product design](/Users/sharmindabadmash/Desktop/projs/journal_proj/docs/product-and-data-design.md) for the reasoning and future path.

## Run Locally

You need Docker Desktop running for Postgres.

Terminal 1: database

```bash
cd /Users/sharmindabadmash/Desktop/projs/journal_proj
docker compose up -d postgres
```

This project maps Postgres to local port `5433` so it can coexist with another project using `5432`.

Terminal 2: API

```bash
cd /Users/sharmindabadmash/Desktop/projs/journal_proj/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

FastAPI documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

Terminal 3: frontend

```bash
cd /Users/sharmindabadmash/Desktop/projs/journal_proj/frontend
npm install
cp .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## AI Credentials

The app runs without an API key in `local-fallback` mode, which preserves the API flow and evidence display without calling a model. For real LLM insights, copy `backend/.env.example` to `backend/.env` and set `OPENAI_API_KEY`. The app uses the Responses API for insight generation and is prepared for `text-embedding-3-small` embeddings when the background indexing worker is enabled.

## Data Engineering

The `analytics/` directory contains a dbt project with:

- Bronze application-event model
- Silver cleaned journal-entry model
- Gold weekly activity mart
- Data-quality tests for keys, users, and dates

Copy `analytics/profiles.yml.example` into your dbt profile location, then run `dbt run` and `dbt test`.

## Current Endpoints

- `POST /api/v1/entries`
- `GET /api/v1/entries?start=&end=&limit=&offset=`
- `GET /health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `PATCH /api/v1/entries/{id}`
- `DELETE /api/v1/entries/{id}`
- `POST /api/v1/entries/{id}/suggest-themes`
- `POST /api/v1/entries/{id}/embed`
- `POST /api/v1/insights`

The exact request contract is in [data-contract.md](/Users/sharmindabadmash/Desktop/projs/journal_proj/docs/data-contract.md).

## Project Phases

| Phase | Outcome | Status |
| --- | --- | --- |
| 0 | Product direction and stable free-form entry contract | Complete |
| 1 | Next.js entry form, FastAPI API, Postgres model, date-filtered timeline | Complete and running locally |
| 2 | Edit/delete entries, product accounts, and Alembic migration scaffold | Complete |
| 3 | User-requested simple-text insights for a chosen time range | Complete with API-key placeholder and local fallback |
| 4 | RAG retrieval-ready chunks, pgvector storage, and cited excerpts | Complete foundation; background embedding indexing awaits API key |
| 5 | Optional theme suggestions and comparisons across time | Theme suggestions complete; comparisons remain a future enhancement |
| 6 | dbt Bronze/Silver/Gold analytics layer and data-quality tests | Complete foundation |

## Verify

```bash
cd /Users/sharmindabadmash/Desktop/projs/journal_proj/backend
.venv/bin/python -m pytest -q

cd /Users/sharmindabadmash/Desktop/projs/journal_proj/frontend
npm run typecheck
npm run build
```
