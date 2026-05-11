from sqlalchemy import Column, Integer, Text, DateTime
from datetime import datetime

from memory.database import Base


class ConversationMemory(Base):

    __tablename__ = "conversation_memory"

    id = Column(Integer, primary_key=True, index=True)

    user_prompt = Column(Text)

    ai_response = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)