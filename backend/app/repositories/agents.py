from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Agent


class AgentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Agent]:
        return list(self.db.scalars(select(Agent).order_by(Agent.id)).all())

    def list_existing(self) -> dict[int, Agent]:
        return {agent.id: agent for agent in self.db.scalars(select(Agent)).all()}
