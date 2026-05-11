from memory.database import SessionLocal
from memory.models import ConversationMemory


def save_interaction(user_prompt, ai_response):

    db = SessionLocal()

    memory = ConversationMemory(
        user_prompt=user_prompt,
        ai_response=str(ai_response)
    )

    db.add(memory)

    db.commit()

    db.close()


def get_recent_memory(limit=5):

    db = SessionLocal()

    memories = (
        db.query(ConversationMemory)
        .order_by(ConversationMemory.created_at.desc())
        .limit(limit)
        .all()
    )

    db.close()

    return memories