# Project checkpoint: 2026-09-23

Repository: `himanshuSharma-13/journal-ai-coach`
Code baseline before this document: `d5c4468` on `main`

## Product decision

This is intended to become a general-purpose journaling product. People write free-form entries. They request simple text reflections when they want them. Mood scores, habits, goals, automatic summaries, and charts are not part of the current experience. Theme suggestions are optional and requested per entry.

## What exists in code

- `frontend/`: Next.js page for registration/sign-in, writing, date-filtered browsing, editing, deleting, theme suggestions, and requested insights. The UI stores its bearer token in browser local storage.
- `backend/`: FastAPI with account registration/login, password hashing, JWT authentication, user-scoped entry queries, entry edit/delete, theme suggestions, and stored insight responses.
- `backend/app/models.py`: users, entries, chunks with optional pgvector embeddings, theme suggestions, insights, and journal events.
- `backend/app/services.py`: text chunking, rule-based theme suggestions, optional OpenAI embedding and Responses calls, and a local fallback when no API key is configured.
- `backend/migrations/`: an initial Alembic migration draft. The API still creates tables with SQLAlchemy on startup.
- `analytics/`: dbt Bronze event view, Silver entry view, Gold weekly activity table, and basic schema tests.
- `docker-compose.yml`: local Postgres with pgvector mapped to port `5433`.

## Verified so far

- The previous build ran backend contract tests (`3 passed`) and a Next.js production build successfully.
- A local account was registered; an entry was saved; a local fallback insight returned with dated evidence.
- The Postgres container was healthy on port `5433` when this checkpoint was written.
- Real OpenAI requests, embedding search, the Alembic migration, and dbt runs have **not** been verified.

## Important gaps before a public release

1. Make migrations the only schema-change path. The initial migration has not been applied or tested, and the API still calls `create_all` on startup. Existing single-user databases need an explicit migration or data-export plan.
2. Finish RAG indexing. Entries are chunked on creation, but embeddings are created only by manually calling `POST /api/v1/entries/{id}/embed` with a valid key. New and edited entries are not automatically indexed.
3. Verify model behavior with an API key. The fallback does not generate an AI insight. The vector path may return no evidence when no chunks have embeddings; the response, citations, and error handling need tests.
4. Reconcile deletion and evidence. Deleting an entry removes its chunks and theme suggestions through database cascades, but already stored insight evidence still contains excerpts from that entry.
5. Test the dbt project against the current database. The models and schema tests have not yet been executed, and no scheduler or pipeline monitor exists.
6. Harden accounts for production: replace the development JWT secret, add a safe token/session strategy, rate limits, password reset, data export, and deployment-specific security checks.
7. Build comparison views and evaluate insight quality with a small set of real, consented journal examples.

## Suggested next sequence

1. Repair and test Alembic migrations against a fresh database, then plan how to preserve any data in the older volume.
2. Add API integration tests for user isolation, entry lifecycle, deletion, and insights.
3. Automate embedding indexing and test vector retrieval with a real API key.
4. Run dbt models/tests locally and connect a useful analytics view to the product.
5. Prepare authentication and privacy controls before inviting external users.

No external credentials are committed. Use the `.env.example` files as configuration templates.
