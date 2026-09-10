from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas import JournalEntryCreate


def test_entry_contract_accepts_valid_entry() -> None:
    entry = JournalEntryCreate(
        content="I completed my planned workout and had more energy than last week.",
        occurred_at=datetime.now(timezone.utc),
    )
    assert entry.source == "manual"


def test_entry_contract_rejects_short_content() -> None:
    with pytest.raises(ValidationError):
        JournalEntryCreate(
            content="Too short",
            occurred_at=datetime.now(timezone.utc),
        )


def test_entry_contract_rejects_naive_timestamps() -> None:
    with pytest.raises(ValidationError):
        JournalEntryCreate(
            content="This is a sufficiently long journal entry for contract validation.",
            occurred_at=datetime.now(),
        )
