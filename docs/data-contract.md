# Data Contract: Journal Entries

This is the stable boundary between the Next.js frontend, FastAPI backend, Postgres database, and future AI/data pipelines.

## Create Entry

`POST /api/v1/entries`

```json
{
  "content": "I had a productive day, but I noticed I avoided starting the hardest task until late in the afternoon.",
  "occurred_at": "2026-09-10T18:30:00+05:30",
  "source": "manual"
}
```

Rules:

- `content`: 20 to 20,000 characters.
- `occurred_at`: ISO 8601 timestamp with a timezone offset.
- `source`: defaults to `manual`.
- The backend generates `id` and `created_at`.

## List Entries

`GET /api/v1/entries?start=2026-09-01T00:00:00Z&end=2026-09-30T23:59:59Z`

Optional pagination parameters are `limit` (maximum 100) and `offset`.

## Future Insight Contract

Future AI output will be validated and stored separately from journal text. It will eventually include a short summary, confidence, and dated evidence references. Themes, habits, and scores are intentionally absent until the product needs them.
