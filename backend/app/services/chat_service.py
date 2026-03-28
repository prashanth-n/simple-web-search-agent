from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.agent.chat_agent import execute_agent_response
from app.agent.registry import AgentProfile
from app.db.models import ChatMessage, ChatThread, User
from app.repositories.messages import MessageRepository
from app.repositories.threads import ThreadRepository
from app.services.run_service import RunService


class ChatService:
    def __init__(
        self,
        db: Session,
        thread_repository: ThreadRepository,
        message_repository: MessageRepository,
        run_service: RunService,
    ) -> None:
        self.db = db
        self.thread_repository = thread_repository
        self.message_repository = message_repository
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

    def send_message(
        self,
        *,
        user: User,
        thread: ChatThread,
        profile: AgentProfile,
        content: str,
    ) -> tuple[ChatMessage, ChatMessage]:
        user_message = self.message_repository.create(
            user_id=user.id,
            thread_id=thread.id,
            role="user",
            content=content,
        )

        response = execute_agent_response(profile=profile, content=content)

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

        self.db.commit()
        self.db.refresh(user_message)
        self.db.refresh(assistant_message)
        self.db.refresh(thread)
        return user_message, assistant_message
