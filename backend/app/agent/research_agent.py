from __future__ import annotations

import logging

from app.tools.scrape import scrape_page
from app.tools.search import search_web
from app.tools.summarize import summarize_content

logger = logging.getLogger(__name__)


def run_research(query: str) -> list[dict[str, str]]:
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
                )
            )
        except Exception as exc:  # pragma: no cover - network failures are non-deterministic
            logger.warning("Failed to process %s: %s", item["link"], exc)

    return structured_results
