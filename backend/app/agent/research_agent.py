from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.agent.registry import AgentProfile
from app.tools.scrape import scrape_page
from app.tools.search import search_web
from app.tools.summarize import summarize_content

logger = logging.getLogger(__name__)


def run_research(profile: AgentProfile, query: str) -> list[dict[str, str]]:
    search_results = search_web(query)
    structured_results: list[dict[str, str]] = []

    for item in search_results:
        try:
            content = scrape_page(item["link"])
            if not content:
                continue
            structured_results.append(
                summarize_content(
                    text=content,
                    source_title=item["title"],
                    source_url=item["link"],
                    system_prompt=profile.system_prompt,
                    model=profile.model,
                )
            )
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to process %s: %s", item["link"], exc)

    return structured_results


def persist_research_run(
    db: Session,
    profile: AgentProfile,
    query: str,
    results: list[dict[str, str]],
) -> None:
    record = profile.run_model(agent_id=profile.id, query=query, results=results)
    db.add(record)
    db.commit()
