"""
Memory manager for Universal AI.

Critical fix
────────────
The old version returned the 5 most recent rows from the WHOLE database,
which caused unrelated chats (e.g. billionaire research) to bleed into
a current coding chat.

This version requires (or strongly recommends) a ``chat_id`` so each
chat session has isolated memory.

Backwards compatible:
- ``save_interaction(...)`` still works without chat_id (uses "default").
- ``get_formatted_memory()`` still works without chat_id (uses "default").
  In the orchestrator we pass the actual chat_id when available.
"""

import logging
from typing import Optional

from memory.database import SessionLocal
from memory.models import ConversationMemory

log = logging.getLogger(__name__)

DEFAULT_CHAT_ID = "default"


# ==========================================
# SAVE INTERACTION
# ==========================================
def save_interaction(
    user_prompt: str,
    ai_response: str,
    chat_id: Optional[str] = None,
    mode: Optional[str] = None,
    intent: Optional[str] = None,
) -> None:
    """
    Persist one user/assistant turn to the database.

    chat_id  → groups turns belonging to the same chat session.
               Pass the frontend chat id (e.g. "1779183537926") to
               keep per-chat memory isolated.
    """
    db = SessionLocal()
    try:
        memory = ConversationMemory(
            chat_id=str(chat_id or DEFAULT_CHAT_ID),
            user_prompt=user_prompt,
            ai_response=str(ai_response),
            mode=mode,
            intent=intent,
        )
        db.add(memory)
        db.commit()
    except Exception as exc:
        db.rollback()
        log.warning("Memory save failed: %s", exc)
    finally:
        db.close()


# ==========================================
# GET RECENT MEMORY (per chat)
# ==========================================
def get_recent_memory(limit: int = 5, chat_id: Optional[str] = None):
    """Return the most recent N turns FOR THE GIVEN CHAT."""
    db = SessionLocal()
    try:
        query = db.query(ConversationMemory)
        if chat_id:
            query = query.filter(ConversationMemory.chat_id == str(chat_id))
        return (
            query.order_by(ConversationMemory.created_at.desc())
                 .limit(limit)
                 .all()
        )
    except Exception as exc:
        log.warning("Memory retrieval failed: %s", exc)
        return []
    finally:
        db.close()


# ==========================================
# FORMAT MEMORY FOR PROMPTS (per chat)
# ==========================================
def get_formatted_memory(limit: int = 5, chat_id: Optional[str] = None) -> str:
    """
    Return a human-readable transcript of the last N turns for the chat.
    Returns empty string when there's nothing — easier for the
    orchestrator to skip empty sections than handle a placeholder.
    """
    memories = get_recent_memory(limit=limit, chat_id=chat_id)
    if not memories:
        return ""

    # DB returned newest-first; reverse so oldest is shown first in prompt.
    memories = list(reversed(memories))

    lines = []
    for m in memories:
        prompt = (m.user_prompt or "").strip()
        reply = (m.ai_response or "").strip()
        if len(reply) > 1200:
            reply = reply[:1200] + " …[truncated]"
        lines.append(f"USER: {prompt}\nASSISTANT: {reply}")
    return "\n\n".join(lines)


# ==========================================
# CLEAR MEMORY (per chat or all)
# ==========================================
def clear_memory(chat_id: Optional[str] = None) -> int:
    """
    Delete memory rows.

    - clear_memory("abc")  → wipes only chat "abc"
    - clear_memory(None)   → wipes EVERYTHING (use with care)

    Returns the number of rows deleted.
    """
    db = SessionLocal()
    try:
        query = db.query(ConversationMemory)
        if chat_id:
            query = query.filter(ConversationMemory.chat_id == str(chat_id))
        count = query.delete(synchronize_session=False)
        db.commit()
        log.info("🗑️  Cleared %d memory rows (chat_id=%s)", count, chat_id or "ALL")
        return count
    except Exception as exc:
        db.rollback()
        log.warning("Memory clear failed: %s", exc)
        return 0
    finally:
        db.close()
