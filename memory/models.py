"""
Database models for Universal AI memory.

Key change vs old version
─────────────────────────
- Added `chat_id` column so each conversation is isolated.
  This fixes the bug where billionaire memory bled into a coding chat.

- Added `mode` and `intent` columns for analytics and smarter
  memory retrieval later (e.g. "show me only my coding turns").

- Replaced deprecated ``datetime.utcnow`` (warning in Py 3.12+) with
  a small ``utcnow_naive`` helper that uses ``datetime.now(UTC)``
  but keeps the column timezone-naive for SQLite compatibility.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Text, DateTime, String, Index

from memory.database import Base


def _utcnow() -> datetime:
    """UTC timestamp without tzinfo (safe for SQLite + modern Python)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ConversationMemory(Base):
    __tablename__ = "conversation_memory"

    id = Column(Integer, primary_key=True, index=True)

    # NEW: groups turns belonging to the same chat session.
    # Default is "default" so existing rows without an id still work.
    chat_id = Column(String(64), nullable=False, default="default", index=True)

    user_prompt = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)

    # Optional metadata — useful for debugging / future filtering
    mode = Column(String(32), nullable=True)
    intent = Column(String(32), nullable=True)

    created_at = Column(DateTime, default=_utcnow, index=True)

    __table_args__ = (
        # Speeds up the common query: latest N memories per chat.
        Index("ix_chat_created", "chat_id", "created_at"),
    )

    def __repr__(self):
        return (
            f"<ConversationMemory("
            f"id={self.id}, "
            f"chat_id={self.chat_id}, "
            f"prompt={self.user_prompt[:30]!r}"
            f")>"
        )
