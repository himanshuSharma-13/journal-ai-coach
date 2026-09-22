"""Product foundation: ownership, entries, retrieval, insights, and events."""
from alembic import op

revision = "0001_product_foundation"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("""
    CREATE TABLE users (id uuid PRIMARY KEY, email varchar(320) UNIQUE NOT NULL, password_hash varchar(255) NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
    CREATE TABLE journal_entries (id uuid PRIMARY KEY, user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE, content text NOT NULL, occurred_at timestamptz NOT NULL, source varchar(40) NOT NULL DEFAULT 'manual', created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
    CREATE TABLE entry_chunks (id uuid PRIMARY KEY, entry_id uuid NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE, chunk_index integer NOT NULL, content text NOT NULL, embedding vector(1536), embedding_model varchar(100), created_at timestamptz NOT NULL DEFAULT now(), CONSTRAINT uq_entry_chunk_index UNIQUE(entry_id, chunk_index));
    CREATE TABLE entry_themes (id uuid PRIMARY KEY, entry_id uuid NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE, theme varchar(50) NOT NULL, confidence double precision NOT NULL, source varchar(40) NOT NULL DEFAULT 'suggested', CONSTRAINT uq_entry_theme UNIQUE(entry_id, theme));
    CREATE TABLE insights (id uuid PRIMARY KEY, user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE, question text NOT NULL, answer text NOT NULL, period_start timestamptz NOT NULL, period_end timestamptz NOT NULL, evidence jsonb NOT NULL DEFAULT '[]', provider varchar(40) NOT NULL, model varchar(100), created_at timestamptz NOT NULL DEFAULT now());
    CREATE TABLE journal_events (id uuid PRIMARY KEY, user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE, event_type varchar(80) NOT NULL, entity_id uuid NOT NULL, payload jsonb NOT NULL DEFAULT '{}', occurred_at timestamptz NOT NULL DEFAULT now());
    CREATE INDEX idx_entries_user_occurred ON journal_entries(user_id, occurred_at DESC);
    CREATE INDEX idx_events_user_type ON journal_events(user_id, event_type, occurred_at DESC);
    """)

def downgrade():
    op.execute("DROP TABLE IF EXISTS journal_events, insights, entry_themes, entry_chunks, journal_entries, users CASCADE")
