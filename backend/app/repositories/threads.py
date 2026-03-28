from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ChatThread


class ThreadRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, user_id: int, agent_id: int, title: str) -> ChatThread:
        thread = ChatThread(user_id=user_id, agent_id=agent_id, title=title)
        self.db.add(thread)
        self.db.flush()
        return thread

    def list_for_user(self, *, user_id: int, agent_id: int) -> list[ChatThread]:
        return list(
            self.db.scalars(
                select(ChatThread)
                .where(ChatThread.user_id == user_id, ChatThread.agent_id == agent_id)
                .order_by(ChatThread.updated_at.desc(), ChatThread.id.desc())
            ).all()
        )

    def get_owned(self, *, thread_id: int, user_id: int) -> ChatThread | None:
        return self.db.scalar(
            select(ChatThread).where(ChatThread.id == thread_id, ChatThread.user_id == user_id)
        )

    def save(self, thread: ChatThread) -> ChatThread:
        self.db.add(thread)
        self.db.flush()
        return thread
