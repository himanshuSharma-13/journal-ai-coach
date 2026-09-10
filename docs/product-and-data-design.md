# Journal AI Coach: Product and Data Design

Status: working design agreed for the MVP. It is a product foundation, not a personal-only tool.

## Product Direction

Journal AI Coach is a general-purpose long-term reflection product. People write journal entries freely, keep a durable record, and request simple text insights only when they choose.

The core rule is:

> The original journal entry is the source of truth. AI may interpret it later, but never edits or replaces it.

## MVP Experience

```text
Write freely
  -> Save entry with its timestamp
  -> Browse entries by date
  -> Ask for a simple insight when enough history exists
  -> Read a short, evidence-backed answer
```

MVP deliberately excludes themes, mood, energy, habits, goals, automatic summaries, and dashboards. We can introduce each only after it has a clear product purpose.

## Current Data Model

### `journal_entries`

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Server-generated stable identifier. |
| `content` | text | Yes | Original free-form journal text, 20-20,000 characters. |
| `occurred_at` | timezone-aware timestamp | Yes | When the entry occurred. Defaults to the current time in the UI. |
| `source` | string | Yes | Starts as `manual`; supports imports later. |
| `created_at` | timezone-aware timestamp | Yes | Server-generated audit timestamp. |

## Current Application Flow

```text
Next.js frontend
  -> POST /api/v1/entries
  -> FastAPI validates the request
  -> Postgres saves the original entry
  -> FastAPI returns the saved record
  -> Frontend refreshes the timeline
```

The timeline uses `GET /api/v1/entries?start=&end=` and returns newest entries first.

## Future Insight Flow

For the first AI version, a person asks an open question such as: "What patterns do you notice in my last month?"

```text
Question + date range
  -> Load entries for the selected period
  -> Later: retrieve the most relevant chunks with RAG
  -> Send only relevant evidence to the model
  -> Return short plain text plus dated source excerpts
```

The insight should be simple text in MVP, not a coaching dashboard. It is generated only when a user asks.

## Features We Intentionally Postpone

- Themes: later AI-suggested or user-confirmed labels after we have real writing data.
- Mood and energy: they can feel overly quantified and are not necessary for meaningful reflection.
- Habits and goals: do not store as separate objects yet.
- Automatic insight generation: insights remain user-requested.
- Charts and progress scores: only add if they make the product more helpful.

## Product Growth Path

```text
Free-form writing
  -> Asked-for text insights
  -> RAG over historical entries
  -> Optional theme suggestions
  -> Evidence-backed comparisons across time
  -> Optional analytics and data pipelines
```

## Open Product Decisions

1. Should the timestamp be editable, or simply default to now and remain hidden most of the time?
2. Should users be able to edit and delete entries in the first release?
3. Should the first insight be an open text question or a few suggested prompts?
4. Should the default insight period be the last 30 days, or should users always choose it?
5. Should insight language be reflective, direct/coaching, or neutral/factual?
6. Will the initial product need accounts immediately, or can we validate the local journaling experience first?

## Guardrails

- Never overwrite original journal text.
- Keep AI output separate from user-authored content.
- Show evidence for any substantive insight.
- Label uncertain conclusions clearly.
- Add authentication, authorization, and encryption before a public deployment.
