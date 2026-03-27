from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent.registry import get_agent_profile
from app.agent.research_agent import persist_research_run, run_research
from app.db.models import Agent
from app.db.session import get_db

router = APIRouter()


@router.get("/health-chec")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/agents")
def list_agents(db: Session = Depends(get_db)) -> dict[str, list[dict[str, str | int]]]:
    agents = db.scalars(select(Agent).order_by(Agent.id)).all()
    return {
        "agents": [
            {
                "id": agent.id,
                "slug": agent.slug,
                "name": agent.name,
                "description": agent.description,
            }
            for agent in agents
        ]
    }


@router.get("/research")
def research(
    query: str = Query(..., min_length=2, description="Research prompt"),
    agent_id: int = Query(..., description="Agent identifier"),
    db: Session = Depends(get_db),
) -> dict:
    profile = get_agent_profile(agent_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Unknown agent.")

    results = run_research(profile, query)
    if not results:
        raise HTTPException(status_code=502, detail="No research results were produced.")

    persist_research_run(db, profile, query, results)

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
