from __future__ import annotations

from sqlalchemy.orm import Session

from app.agent.registry import list_agent_profiles
from app.db.models import Agent
from app.repositories.agents import AgentRepository


def seed_agents(db: Session) -> None:
    repository = AgentRepository(db)
    existing_agents = repository.list_existing()

    for profile in list_agent_profiles():
        agent = existing_agents.get(profile.id)
        if agent is None:
            db.add(
                Agent(
                    id=profile.id,
                    slug=profile.slug,
                    name=profile.name,
                    description=profile.description,
                )
            )
            continue

        agent.slug = profile.slug
        agent.name = profile.name
        agent.description = profile.description

    db.commit()
