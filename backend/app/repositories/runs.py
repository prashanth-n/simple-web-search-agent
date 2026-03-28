from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.agent.registry import AgentProfile


class RunRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_run(
        self,
        *,
        profile: AgentProfile,
        user_id: int,
        query: str,
        results: Any,
    ) -> None:
        record = profile.run_model(
            user_id=user_id,
            agent_id=profile.id,
            query=query,
            results=results,
        )
        self.db.add(record)
        self.db.flush()
