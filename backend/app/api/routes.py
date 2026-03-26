from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.agent.research_agent import run_research
from app.db.models import ResearchQuery
from app.db.session import get_db

router = APIRouter()


@router.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/research")
def research(
    query: str = Query(..., min_length=2, description="Research prompt"),
    db: Session = Depends(get_db),
) -> dict:
    results = run_research(query)
    if not results:
        raise HTTPException(status_code=502, detail="No research results were produced.")

    record = ResearchQuery(query=query, results=results)
    db.add(record)
    db.commit()

    return {"query": query, "results": results}
