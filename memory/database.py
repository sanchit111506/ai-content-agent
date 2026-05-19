"""
Database configuration for Universal AI memory.

Uses SQLite with WAL mode for safer concurrent reads/writes
(WAL = Write-Ahead Logging, lets readers run while a writer commits).
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

# =========================
# DATABASE CONFIG
# =========================
DATABASE_URL = "sqlite:///./ai_memory.db"

# =========================
# ENGINE
# =========================
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# Enable WAL mode + foreign keys for every new SQLite connection.
# WAL improves concurrency; foreign keys keep data integrity.
@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, _connection_record):
    cur = dbapi_connection.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA foreign_keys=ON;")
    cur.close()


# =========================
# SESSION
# =========================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# =========================
# BASE
# =========================
Base = declarative_base()
