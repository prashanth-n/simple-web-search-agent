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
    for token in query.split():
        cleaned = token.strip(" ,.:;!?()[]{}")
        candidate = cleaned.removeprefix("$")
        if 1 <= len(candidate) <= 5 and candidate.isalpha() and candidate == candidate.upper():
            return candidate
    raise ValueError("Please include a stock ticker symbol such as AAPL or MSFT.")


def _resolve_symbol(content: str, memory_facts: list[dict[str, Any]]) -> str:
    try:
        return _extract_symbol(content)
    except ValueError:
        for fact in memory_facts:
            metadata = fact.get("metadata") if isinstance(fact, dict) else {}
            if not isinstance(metadata, dict):
                continue
            if str(metadata.get("key")) == "ticker":
                value = str(metadata.get("value") or "").strip().upper()
                if value:
                    return value
        raise


def _contextual_query(content: str, context_block: str) -> str:
    if not context_block.strip():
        return content
    return f"{content}\n\nRelevant thread context:\n{context_block.strip()}"


def execute_agent_response(
    profile: AgentProfile,
    content: str,
    *,
    context_block: str = "",
    memory_facts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    memory_facts = memory_facts or []
    if profile.mode == "financial":
        symbol = _resolve_symbol(content, memory_facts)
        overview = get_company_overview(symbol)
        chart = get_daily_series(symbol)
        assistant_content = summarize_financial_snapshot(
            query=_contextual_query(content, context_block),
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

    effective_query = _contextual_query(content, context_block)
    results = run_research(profile, effective_query)
    if not results:
        raise ValueError("No research results were produced.")

    if profile.mode == "competitor":
        analysis = summarize_competitor_analysis(effective_query, results, profile.system_prompt, profile.model)
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
        effective_query,
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
