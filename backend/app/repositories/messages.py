from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ChatMessage


class MessageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: int,
        thread_id: int,
        role: str,
        content: str,
        message_type: str = "text",
        metadata: dict[str, Any] | None = None,
    ) -> ChatMessage:
        message = ChatMessage(
            user_id=user_id,
            thread_id=thread_id,
            role=role,
            content=content,
            message_type=message_type,
            metadata=metadata or {},
        )
        self.db.add(message)
        self.db.flush()
        return message

    def list_for_thread(self, *, thread_id: int, user_id: int) -> list[ChatMessage]:
        return list(
            self.db.scalars(
                select(ChatMessage)
                .where(ChatMessage.thread_id == thread_id, ChatMessage.user_id == user_id)
                .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
            ).all()
        )
