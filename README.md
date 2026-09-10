# Journal AI Coach

A general-purpose product for free-form journaling and long-term, user-requested AI reflection.

## Repository Layout

```text
frontend/                 Next.js + TypeScript client
backend/                  FastAPI + SQLAlchemy service
docs/                     Product design and API/data contracts
docker-compose.yml        Local Postgres infrastructure
```

## MVP Scope

The first release is intentionally small:

- Write a free-form journal entry.
- Save the original entry permanently in Postgres.
- Browse the timeline and filter it by date.
- Later, ask for a short text insight based on the entries you choose.

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

## Current Endpoints

- `POST /api/v1/entries`
- `GET /api/v1/entries?start=&end=&limit=&offset=`
- `GET /health`

The exact request contract is in [data-contract.md](/Users/sharmindabadmash/Desktop/projs/journal_proj/docs/data-contract.md).

## Project Phases

| Phase | Outcome | Status |
| --- | --- | --- |
| 0 | Product direction and stable free-form entry contract | Complete |
| 1 | Next.js entry form, FastAPI API, Postgres model, date-filtered timeline | Complete and running locally |
| 2 | Edit/delete entries, basic product accounts, and production migrations | Not started |
| 3 | User-requested simple-text insights for a chosen time range | Not started |
| 4 | RAG retrieval over historical entries with cited excerpts | Not started |
| 5 | Optional AI theme suggestions and comparisons across time | Not started |
| 6 | Optional analytics, data pipelines, and dashboards | Not started |

## Verify

```bash
cd /Users/sharmindabadmash/Desktop/projs/journal_proj/backend
.venv/bin/python -m pytest -q

cd /Users/sharmindabadmash/Desktop/projs/journal_proj/frontend
npm run typecheck
npm run build
```
