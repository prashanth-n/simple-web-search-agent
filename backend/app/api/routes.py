from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agent.registry import get_agent_profile
from app.agent.research_agent import run_research
from app.auth.dependencies import get_current_user
from app.db.models import Agent, ChatMessage, User
from app.db.session import get_db
from app.repositories.agents import AgentRepository
from app.repositories.memories import MemoryRepository
from app.repositories.messages import MessageRepository
from app.repositories.runs import RunRepository
from app.repositories.threads import ThreadRepository
from app.services.chat_service import ChatService
from app.services.run_service import RunService

router = APIRouter()


class ThreadCreateRequest(BaseModel):
    agent_id: int
    title: str | None = Field(default=None, max_length=200)


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


def _serialize_agent(agent: Agent | Any) -> dict[str, str | int]:
    return {
        "id": agent.id,
        "slug": agent.slug,
        "name": agent.name,
        "description": agent.description,
    }


def _serialize_message(message: ChatMessage) -> dict[str, Any]:
    return {
        "id": message.id,
        "thread_id": message.thread_id,
        "role": message.role,
        "content": message.content,
        "message_type": message.message_type,
        "metadata": message.metadata,
        "created_at": message.created_at.isoformat() if message.created_at else None,
    }


def _build_chat_service(db: Session) -> ChatService:
    return ChatService(
        db,
        ThreadRepository(db),
        MessageRepository(db),
        MemoryRepository(db),
        RunService(RunRepository(db)),
    )


@router.get("/health-check")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/agents")
def list_agents(db: Session = Depends(get_db)) -> dict[str, list[dict[str, str | int]]]:
    agents = AgentRepository(db).list_all()
    return {"agents": [_serialize_agent(agent) for agent in agents]}


@router.get("/research")
def research(
    query: str = Query(..., min_length=2, description="Research prompt"),
    agent_id: int = Query(..., description="Agent identifier"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    profile = get_agent_profile(agent_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Unknown agent.")

    results = run_research(profile, query)
    if not results:
        raise HTTPException(status_code=502, detail="No research results were produced.")

    run_service = RunService(RunRepository(db))
    run_service.persist(profile=profile, user_id=user.id, query=query, results=results)
    db.commit()

    return {
        "agent": {
            "id": profile.id,
            "slug": profile.slug,
            "name": profile.name,
            "description": profile.description,
        },
        "query": query,
        "results": results,
    }


@router.get("/threads")
def get_threads(
    agent_id: int = Query(..., description="Agent identifier"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, list[dict[str, Any]]]:
    profile = get_agent_profile(agent_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Unknown agent.")

    chat_service = _build_chat_service(db)
    threads = chat_service.list_threads(user_id=user.id, agent_id=agent_id)
    return {
        "threads": [
            {
                "id": thread.id,
                "agent_id": thread.agent_id,
                "title": thread.title,
                "created_at": thread.created_at.isoformat() if thread.created_at else None,
                "updated_at": thread.updated_at.isoformat() if thread.updated_at else None,
            }
            for thread in threads
        ]
    }


@router.post("/threads")
def post_thread(
    payload: ThreadCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    profile = get_agent_profile(payload.agent_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Unknown agent.")

    title = (payload.title or "New chat").strip() or "New chat"
    chat_service = _build_chat_service(db)
    thread = chat_service.create_thread(user_id=user.id, agent_id=payload.agent_id, title=title)
    return {
        "thread": {
            "id": thread.id,
            "agent_id": thread.agent_id,
            "title": thread.title,
            "created_at": thread.created_at.isoformat() if thread.created_at else None,
            "updated_at": thread.updated_at.isoformat() if thread.updated_at else None,
        }
    }


@router.get("/threads/{thread_id}/messages")
def get_thread_messages(
    thread_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, list[dict[str, Any]]]:
    chat_service = _build_chat_service(db)
    thread = chat_service.get_thread(thread_id=thread_id, user_id=user.id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found.")

    messages = chat_service.list_messages(thread_id=thread_id, user_id=user.id)
    return {"messages": [_serialize_message(message) for message in messages]}


@router.post("/threads/{thread_id}/messages")
def post_thread_message(
    thread_id: int,
    payload: MessageCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    chat_service = _build_chat_service(db)
    thread = chat_service.get_thread(thread_id=thread_id, user_id=user.id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found.")

    profile = get_agent_profile(thread.agent_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Unknown agent.")

    try:
        user_message, assistant_message = chat_service.send_message(
            user=user,
            thread=thread,
            profile=profile,
            content=payload.content,
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        db.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "thread": {
            "id": thread.id,
            "agent_id": thread.agent_id,
            "title": thread.title,
            "created_at": thread.created_at.isoformat() if thread.created_at else None,
            "updated_at": thread.updated_at.isoformat() if thread.updated_at else None,
        },
        "messages": {
            "user": _serialize_message(user_message),
            "assistant": _serialize_message(assistant_message),
        },
    }


@router.get("/threads/{thread_id}/memory")
def get_thread_memory(
    thread_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    chat_service = _build_chat_service(db)
    thread = chat_service.get_thread(thread_id=thread_id, user_id=user.id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found.")

    return {"memory": chat_service.get_memory_payload(thread_id=thread_id, user_id=user.id)}
