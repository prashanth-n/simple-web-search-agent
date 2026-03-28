from __future__ import annotations

import json
import re
from typing import Any

from app.agent.registry import AgentProfile
from app.core.llm import generate_json, generate_text
from app.db.models import ChatMemory, ChatMessage, ChatThread
from app.repositories.memories import MemoryRepository

RECENT_MESSAGE_WINDOW = 12
FACT_LIMIT = 6


def _format_transcript(messages: list[ChatMessage]) -> str:
    return "\n".join(f"{message.role}: {message.content}" for message in messages)


def _safe_json_loads(payload: str) -> dict[str, Any]:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _fallback_summary(messages: list[ChatMessage]) -> str:
    if not messages:
        return ""
    segments = [f"{message.role}: {message.content.strip()}" for message in messages[-6:]]
    return " | ".join(segment[:180] for segment in segments if segment)


def _fallback_fact_entries(profile: AgentProfile, messages: list[ChatMessage]) -> list[dict[str, Any]]:
    transcript = " ".join(message.content for message in messages[-8:])
    facts: list[dict[str, Any]] = []

    ticker_match = re.search(r"\b[A-Z]{1,5}\b", transcript)
    if profile.mode == "financial" and ticker_match:
        facts.append(
            {
                "content": f"Primary ticker in this thread: {ticker_match.group(0)}.",
                "metadata": {"key": "ticker", "label": "Ticker", "value": ticker_match.group(0)},
            }
        )

    if messages:
        facts.append(
            {
                "content": f"Latest user goal: {messages[-1].content.strip()}",
                "metadata": {"key": "latest_goal", "label": "Goal", "value": messages[-1].content.strip()},
            }
        )

    return facts[:FACT_LIMIT]


class MemoryService:
    def __init__(self, memory_repository: MemoryRepository) -> None:
        self.memory_repository = memory_repository

    def list_memory(self, *, user_id: int, thread_id: int) -> list[ChatMemory]:
        return self.memory_repository.list_for_thread(user_id=user_id, thread_id=thread_id)

    def build_context_block(self, *, user_id: int, thread_id: int) -> str:
        memories = self.list_memory(user_id=user_id, thread_id=thread_id)
        summary = next((item for item in memories if item.memory_type == "summary"), None)
        facts = [item for item in memories if item.memory_type == "fact"]

        sections: list[str] = []
        if summary and summary.content.strip():
            sections.append(f"Thread summary:\n{summary.content.strip()}")

        if facts:
            fact_lines = [f"- {fact.content.strip()}" for fact in facts if fact.content.strip()]
            if fact_lines:
                sections.append("Known facts:\n" + "\n".join(fact_lines))

        return "\n\n".join(sections).strip()

    def get_context_payload(self, *, user_id: int, thread_id: int) -> dict[str, Any]:
        memories = self.list_memory(user_id=user_id, thread_id=thread_id)
        summary = next((item for item in memories if item.memory_type == "summary"), None)
        facts = [item for item in memories if item.memory_type == "fact"]
        return {
            "summary": summary.content if summary else "",
            "facts": [
                {
                    "id": fact.id,
                    "content": fact.content,
                    "metadata": fact.metadata,
                    "updated_at": fact.updated_at.isoformat() if fact.updated_at else None,
                }
                for fact in facts
            ],
        }

    def refresh_thread_memory(
        self,
        *,
        user_id: int,
        thread: ChatThread,
        profile: AgentProfile,
        messages: list[ChatMessage],
    ) -> None:
        if not messages:
            return

        summary_content = self._build_summary(profile=profile, messages=messages)
        self.memory_repository.replace_summary(
            user_id=user_id,
            thread_id=thread.id,
            agent_id=thread.agent_id,
            content=summary_content,
            metadata={"message_count": len(messages)},
            source_message_id=messages[-1].id,
        )

        facts = self._build_fact_entries(profile=profile, messages=messages)
        self.memory_repository.replace_facts(
            user_id=user_id,
            thread_id=thread.id,
            agent_id=thread.agent_id,
            facts=facts,
            source_message_id=messages[-1].id,
        )

    def _build_summary(self, *, profile: AgentProfile, messages: list[ChatMessage]) -> str:
        transcript = _format_transcript(messages)
        prompt = f"""
You are maintaining compact chat memory for an agent conversation.
Write a concise thread summary in 4 to 6 sentences.
Keep it factual, mention the user's current objective, notable prior conclusions, and any unresolved follow-up.
Agent mode: {profile.mode}

Transcript:
{transcript}
""".strip()

        try:
            summary = generate_text(prompt, model=profile.model)
        except Exception:
            summary = ""

        return summary.strip() or _fallback_summary(messages)

    def _build_fact_entries(self, *, profile: AgentProfile, messages: list[ChatMessage]) -> list[dict[str, Any]]:
        transcript = _format_transcript(messages[-RECENT_MESSAGE_WINDOW:])
        prompt = f"""
Extract up to {FACT_LIMIT} reusable facts from this thread.
Return JSON with one key: facts.
Each fact must be an object with:
- content
- metadata: object with keys key, label, value

Rules:
- include only facts that help future replies in the same thread
- prefer user goals, entities, products, competitors, ticker symbols, metrics, constraints, and timeframe
- do not repeat the same fact in multiple ways
- facts must be short and specific
Agent mode: {profile.mode}

Transcript:
{transcript}
""".strip()

        try:
            parsed = _safe_json_loads(generate_json(prompt, model=profile.model))
            candidate_facts = parsed.get("facts")
        except Exception:
            candidate_facts = None

        if not isinstance(candidate_facts, list):
            return _fallback_fact_entries(profile, messages)

        facts: list[dict[str, Any]] = []
        seen_keys: set[str] = set()
        for item in candidate_facts:
            if not isinstance(item, dict):
                continue
            content = str(item.get("content") or "").strip()
            metadata = item.get("metadata")
            if not isinstance(metadata, dict):
                metadata = {}
            key = str(metadata.get("key") or content).strip().lower()
            if not content or not key or key in seen_keys:
                continue
            seen_keys.add(key)
            facts.append({"content": content, "metadata": metadata})
            if len(facts) >= FACT_LIMIT:
                break

        return facts or _fallback_fact_entries(profile, messages)
