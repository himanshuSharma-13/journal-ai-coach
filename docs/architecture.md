# Architecture Notes

## Core Idea

Your app should not depend on a model "remembering" six months of conversation.

Instead, memory should be made of:

- raw journal entries stored by the FastAPI service in Postgres
- chunk embeddings for retrieval
- theme scores for structured analysis
- weekly and monthly snapshots for compressed long-term context

## Query Flow

Example question:

`How has my gym discipline changed in the last 6 months?`

The system should:

1. Call the FastAPI entry API with theme = `gym`
2. Retrieve top matching chunks by vector similarity
3. Pull the latest weekly/monthly snapshots for gym
4. Send only that evidence to the model
5. Ask for grounded insights, trend summary, and confidence

## Why Snapshots Matter

If you only retrieve raw chunks, the app becomes noisy as your data grows.

Snapshots give you:

- compressed context
- better historical continuity
- lower cost
- more stable answers across time

## Suggested Milestones

### Milestone 1

Store journal entries and display them.

### Milestone 2

Add embeddings and semantic retrieval.

### Milestone 3

Add theme classification and trend scoring.

### Milestone 4

Generate weekly and monthly summaries automatically.

### Milestone 5

Add charts, comparisons, and "show me evidence" UI.
