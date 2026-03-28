from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import ChatMemory


class MemoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_thread(self, *, user_id: int, thread_id: int) -> list[ChatMemory]:
        return list(
            self.db.scalars(
                select(ChatMemory)
                .where(ChatMemory.user_id == user_id, ChatMemory.thread_id == thread_id)
                .order_by(ChatMemory.memory_type.asc(), ChatMemory.id.asc())
            ).all()
        )

    def get_summary(self, *, user_id: int, thread_id: int) -> ChatMemory | None:
        return self.db.scalar(
            select(ChatMemory).where(
                ChatMemory.user_id == user_id,
                ChatMemory.thread_id == thread_id,
                ChatMemory.memory_type == "summary",
            )
        )

    def replace_summary(
        self,
        *,
        user_id: int,
        thread_id: int,
        agent_id: int,
        content: str,
        metadata: dict | None = None,
        source_message_id: int | None = None,
    ) -> ChatMemory:
        memory = self.get_summary(user_id=user_id, thread_id=thread_id)
        if memory is None:
            memory = ChatMemory(
                user_id=user_id,
                thread_id=thread_id,
                agent_id=agent_id,
                memory_type="summary",
                content=content,
                metadata=metadata or {},
                source_message_id=source_message_id,
            )
        else:
            memory.agent_id = agent_id
            memory.content = content
            memory.metadata = metadata or {}
            memory.source_message_id = source_message_id

        self.db.add(memory)
        self.db.flush()
        return memory

    def replace_facts(
        self,
        *,
        user_id: int,
        thread_id: int,
        agent_id: int,
        facts: list[dict],
        source_message_id: int | None = None,
    ) -> list[ChatMemory]:
        self.db.execute(
            delete(ChatMemory).where(
                ChatMemory.user_id == user_id,
                ChatMemory.thread_id == thread_id,
                ChatMemory.memory_type == "fact",
            )
        )

        records: list[ChatMemory] = []
        for fact in facts:
            content = str(fact.get("content") or "").strip()
            if not content:
                continue

            memory = ChatMemory(
                user_id=user_id,
                thread_id=thread_id,
                agent_id=agent_id,
                memory_type="fact",
                content=content,
                metadata=fact.get("metadata") or {},
                source_message_id=source_message_id,
            )
            self.db.add(memory)
            records.append(memory)

        self.db.flush()
        return records
