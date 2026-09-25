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

The current local prototype supports:

- Write a free-form journal entry.
- Save the original entry permanently in Postgres.
- Browse the timeline and filter it by date.
- Create an account and keep journal data isolated per user.
- Edit or delete entries and their chunks and theme suggestions.
- Request a short evidence-backed insight for a date range.
- Generate optional theme suggestions without requiring themes during writing.
- Create text chunks and analytics events for future RAG and pipelines.

Themes are suggested on request; mood/energy tracking, habits, dashboards, and automatic AI summaries are deferred. See [the product design](docs/product-and-data-design.md) and [the current checkpoint](docs/checkpoint-2026-09-23.md).

## Run Locally

You need Docker Desktop running for Postgres.

Terminal 1: database

```bash
cd /Users/sharmindabadmash/Documents/projs/journal_proj
docker compose up -d postgres
```

This project maps Postgres to local port `5433` so it can coexist with another project using `5432`.

Terminal 2: API

```bash
cd /Users/sharmindabadmash/Documents/projs/journal_proj/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

FastAPI documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

Terminal 3: frontend

```bash
cd /Users/sharmindabadmash/Documents/projs/journal_proj/frontend
npm install
cp .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## AI Credentials

The app runs without an API key in `local-fallback` mode. This returns entry counts and evidence, not an AI interpretation. For model-generated insights, copy `backend/.env.example` to `backend/.env` and set `GROQ_API_KEY`. The backend uses Groq's Responses API for requested reflections and selects up to 30 entries from the chosen date range. The optional `/embed` endpoint still requires a separate `OPENAI_API_KEY`; embeddings are not used by the current insight flow. Automatic indexing and long-term retrieval are not implemented yet. Keep keys in the backend `.env`, which Git ignores.

## Data Engineering

The `analytics/` directory contains a dbt project with:

- Bronze application-event model
- Silver cleaned journal-entry model
- Gold weekly activity mart
- Data-quality tests for keys, users, and dates

These models and tests are present but have not been run with dbt yet. See [the checkpoint](docs/checkpoint-2026-09-23.md) before using them as product analytics.

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

The original entry contract is in [data-contract.md](docs/data-contract.md); the newer auth and insight endpoints are described by FastAPI at `/docs`.

## Project Phases

| Phase | Outcome | Status |
| --- | --- | --- |
| 0 | Product direction and free-form entry contract | Documented |
| 1 | Journal entry API, form, date-filtered timeline | Implemented and locally exercised |
| 2 | Accounts, edit/delete, versioned migrations | API and UI implemented; migration path needs repair and testing |
| 3 | User-requested text insights | Groq model path and local fallback |
| 4 | RAG | Chunk storage and optional manual embedding endpoint; vector retrieval is not part of the current insight flow |
| 5 | Theme suggestions and comparisons | Rule-based suggestions present; comparisons not built |
| 6 | Analytics | dbt models and tests drafted; dbt run not verified |

## Verify

```bash
cd /Users/sharmindabadmash/Documents/projs/journal_proj/backend
.venv/bin/python -m pytest -q

cd /Users/sharmindabadmash/Documents/projs/journal_proj/frontend
npm run typecheck
npm run build
```
