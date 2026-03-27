from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent.registry import list_agent_profiles
from app.db.models import Agent


def seed_agents(db: Session) -> None:
    existing_ids = set(db.scalars(select(Agent.id)).all())

    for profile in list_agent_profiles():
        if profile.id in existing_ids:
            continue

        db.add(
            Agent(
                id=profile.id,
                slug=profile.slug,
                name=profile.name,
                description=profile.description,
            )
        )

    db.commit()
