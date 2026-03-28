from __future__ import annotations

from typing import Any

from app.agent.registry import AgentProfile
from app.agent.research_agent import run_research
from app.tools.finance import get_company_overview, get_daily_series
from app.tools.summarize import (
    summarize_competitor_analysis,
    summarize_financial_snapshot,
    summarize_research_results,
)


def _extract_symbol(query: str) -> str:
    tokens = [token.strip(" ,.:;!?()[]{}").upper() for token in query.split()]
    for token in tokens:
        if 1 <= len(token) <= 5 and token.isalpha():
            return token
    raise ValueError("Please include a stock ticker symbol such as AAPL or MSFT.")


def execute_agent_response(profile: AgentProfile, content: str) -> dict[str, Any]:
    if profile.mode == "financial":
        symbol = _extract_symbol(content)
        overview = get_company_overview(symbol)
        chart = get_daily_series(symbol)
        assistant_content = summarize_financial_snapshot(
            query=content,
            company_overview=overview,
            chart_data=chart,
            system_prompt=profile.system_prompt,
            model=profile.model,
        )
        metadata = {
            "ticker": symbol,
            "company": overview.get("company", symbol),
            "chart": chart,
            "snapshot": overview,
        }
        return {
            "content": assistant_content,
            "message_type": "financial_snapshot",
            "metadata": metadata,
            "run_payload": metadata,
        }

    results = run_research(profile, content)
    if not results:
        raise ValueError("No research results were produced.")

    if profile.mode == "competitor":
        analysis = summarize_competitor_analysis(content, results, profile.system_prompt, profile.model)
        metadata = {
            "company_or_product": analysis["company_or_product"],
            "competitors": analysis["competitors"],
            "sources": analysis["sources"],
            "results": results,
        }
        return {
            "content": analysis["summary"],
            "message_type": "research_results",
            "metadata": metadata,
            "run_payload": metadata,
        }

    assistant_content = summarize_research_results(
        content,
        results,
        profile.system_prompt,
        profile.model,
    )
    metadata = {"results": results}
    return {
        "content": assistant_content,
        "message_type": "research_results",
        "metadata": metadata,
        "run_payload": metadata,
    }
