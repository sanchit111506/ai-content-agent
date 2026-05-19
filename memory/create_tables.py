"""
One-shot script to create / migrate memory tables.

Run once after pulling the new models:
    python -m memory.create_tables

What it does
────────────
1. Creates any missing tables.
2. If the table already exists from the OLD schema (no chat_id column),
   adds the new columns in-place so you don't lose existing rows.
"""

from sqlalchemy import inspect, text

from memory.database import engine
from memory.models import Base, ConversationMemory


def _column_names(table_name: str) -> set[str]:
    insp = inspect(engine)
    if table_name not in insp.get_table_names():
        return set()
    return {c["name"] for c in insp.get_columns(table_name)}


def _add_missing_columns():
    """Add new columns to an existing conversation_memory table if needed."""
    existing = _column_names("conversation_memory")
    if not existing:
        return  # Table doesn't exist yet — create_all will handle it

    statements = []
    if "chat_id" not in existing:
        statements.append(
            "ALTER TABLE conversation_memory "
            "ADD COLUMN chat_id VARCHAR(64) NOT NULL DEFAULT 'default'"
        )
    if "mode" not in existing:
        statements.append(
            "ALTER TABLE conversation_memory ADD COLUMN mode VARCHAR(32)"
        )
    if "intent" not in existing:
        statements.append(
            "ALTER TABLE conversation_memory ADD COLUMN intent VARCHAR(32)"
        )

    if not statements:
        print("✅ Schema already up to date.")
        return

    with engine.begin() as conn:
        for sql in statements:
            print(f"🔧 Running: {sql}")
            conn.execute(text(sql))

        # Try to create the supporting index (safe to ignore if it exists)
        try:
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_chat_created "
                "ON conversation_memory (chat_id, created_at)"
            ))
        except Exception as exc:
            print(f"⚠️  Index creation skipped: {exc}")

    print("✅ Migration complete — old rows now have chat_id='default'.")


def main() -> None:
    print("📁 Creating any missing tables…")
    Base.metadata.create_all(bind=engine)
    print("📁 Checking for schema upgrades…")
    _add_missing_columns()
    print("🎉 Done.")


if __name__ == "__main__":
    main()
