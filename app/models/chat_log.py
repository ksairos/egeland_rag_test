from datetime import datetime
from sqlalchemy import Text, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(100), index=True)
    request_type: Mapped[str] = mapped_column(String(50), default="text") # Тип запроса (text, audio, image)
    user_query: Mapped[str] = mapped_column(Text, nullable=True)
    ai_response: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ChatLog(user={self.user_id}, type={self.request_type})>"