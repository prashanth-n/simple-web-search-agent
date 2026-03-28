from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.agent.chat_agent import execute_agent_response
from app.agent.registry import AgentProfile
from app.db.models import ChatMessage, ChatThread, User
from app.repositories.memories import MemoryRepository
from app.repositories.messages import MessageRepository
from app.repositories.threads import ThreadRepository
from app.services.memory_service import MemoryService, RECENT_MESSAGE_WINDOW
from app.services.run_service import RunService


class ChatService:
    def __init__(
        self,
        db: Session,
        thread_repository: ThreadRepository,
        message_repository: MessageRepository,
        memory_repository: MemoryRepository,
        run_service: RunService,
    ) -> None:
        self.db = db
        self.thread_repository = thread_repository
        self.message_repository = message_repository
        self.memory_service = MemoryService(memory_repository)
        self.run_service = run_service

    def create_thread(self, *, user_id: int, agent_id: int, title: str) -> ChatThread:
        thread = self.thread_repository.create(user_id=user_id, agent_id=agent_id, title=title)
        self.db.commit()
        self.db.refresh(thread)
        return thread

    def list_threads(self, *, user_id: int, agent_id: int) -> list[ChatThread]:
        return self.thread_repository.list_for_user(user_id=user_id, agent_id=agent_id)

    def get_thread(self, *, thread_id: int, user_id: int) -> ChatThread | None:
        return self.thread_repository.get_owned(thread_id=thread_id, user_id=user_id)

    def list_messages(self, *, thread_id: int, user_id: int) -> list[ChatMessage]:
        return self.message_repository.list_for_thread(thread_id=thread_id, user_id=user_id)

    def get_memory_payload(self, *, thread_id: int, user_id: int) -> dict:
        return self.memory_service.get_context_payload(user_id=user_id, thread_id=thread_id)

    def send_message(
        self,
        *,
        user: User,
        thread: ChatThread,
        profile: AgentProfile,
        content: str,
    ) -> tuple[ChatMessage, ChatMessage]:
        recent_messages = self.message_repository.list_recent_for_thread(
            thread_id=thread.id,
            user_id=user.id,
            limit=RECENT_MESSAGE_WINDOW,
        )
        memory_payload = self.memory_service.get_context_payload(user_id=user.id, thread_id=thread.id)
        context_block = self.memory_service.build_context_block(user_id=user.id, thread_id=thread.id)

        user_message = self.message_repository.create(
            user_id=user.id,
            thread_id=thread.id,
            role="user",
            content=content,
        )

        response = execute_agent_response(
            profile=profile,
            content=content,
            context_block=context_block or _serialize_recent_messages(recent_messages),
            memory_facts=memory_payload["facts"],
        )

        self.run_service.persist(
            profile=profile,
            user_id=user.id,
            query=content,
            results=response["run_payload"],
        )

        assistant_message = self.message_repository.create(
            user_id=user.id,
            thread_id=thread.id,
            role="assistant",
            content=response["content"],
            message_type=response["message_type"],
            metadata=response["metadata"],
        )

        thread.updated_at = datetime.now(timezone.utc)
        self.thread_repository.save(thread)

        all_messages = self.message_repository.list_for_thread(thread_id=thread.id, user_id=user.id)
        self.memory_service.refresh_thread_memory(
            user_id=user.id,
            thread=thread,
            profile=profile,
            messages=all_messages,
        )

        self.db.commit()
        self.db.refresh(user_message)
        self.db.refresh(assistant_message)
        self.db.refresh(thread)
        return user_message, assistant_message


def _serialize_recent_messages(messages: list[ChatMessage]) -> str:
    return "\n".join(f"{message.role}: {message.content}" for message in messages).strip()
