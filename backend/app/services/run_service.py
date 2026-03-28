from __future__ import annotations

from typing import Any

from app.agent.registry import AgentProfile
from app.repositories.runs import RunRepository


class RunService:
    def __init__(self, run_repository: RunRepository) -> None:
        self.run_repository = run_repository

    def persist(self, *, profile: AgentProfile, user_id: int, query: str, results: Any) -> None:
        self.run_repository.create_run(
            profile=profile,
            user_id=user_id,
            query=query,
            results=results,
        )
