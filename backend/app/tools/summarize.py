from __future__ import annotations

import json
from typing import Any

from app.core.llm import generate_json, generate_text


def summarize_content(
    text: str,
    source_title: str,
    source_url: str,
    system_prompt: str,
    model: str,
) -> dict[str, str]:
    prompt = f"""
{system_prompt}

Return JSON with keys: title, summary, source.

Rules:
- title: concise human-readable title
- summary: 2 to 4 sentences, factual, no markdown
- source: must exactly equal the supplied source URL

Source title: {source_title}
Source URL: {source_url}
Article content:
{text}
""".strip()

    response = generate_json(prompt, model=model)

    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        parsed = {}

    title = str(parsed.get("title") or source_title).strip() or source_title
    summary = str(parsed.get("summary") or text[:400]).strip()
    source = str(parsed.get("source") or source_url).strip() or source_url

    return {"title": title, "summary": summary, "source": source}


def summarize_research_results(query: str, results: list[dict[str, str]], system_prompt: str, model: str) -> str:
    result_lines = "\n".join(
        f"- {item['title']}: {item['summary']} ({item['source']})" for item in results[:5]
    )
    prompt = f"""
{system_prompt}

You are responding in a chat thread. Summarize the research findings for the user query below.
Keep the answer concise, useful, and grounded in the supplied findings.

User query: {query}
Findings:
{result_lines}
""".strip()
    return generate_text(prompt, model=model) or "I gathered web research results for your request."


def summarize_competitor_analysis(
    query: str,
    results: list[dict[str, str]],
    system_prompt: str,
    model: str,
) -> dict[str, Any]:
    result_lines = "\n".join(
        f"- {item['title']}: {item['summary']} ({item['source']})" for item in results[:6]
    )
    prompt = f"""
{system_prompt}

Return JSON with keys:
- company_or_product
- summary
- competitors: array of objects with keys name, positioning, strengths, weaknesses
- sources: array of source URLs

Base every field on the supplied findings only.

User query: {query}
Findings:
{result_lines}
""".strip()

    response = generate_json(prompt, model=model)
    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        parsed = {}

    competitors = parsed.get("competitors")
    if not isinstance(competitors, list):
        competitors = []

    sources = parsed.get("sources")
    if not isinstance(sources, list):
        sources = [item["source"] for item in results[:5]]

    summary = str(parsed.get("summary") or "").strip()
    if not summary:
        summary = summarize_research_results(query, results, system_prompt, model)

    return {
        "company_or_product": str(parsed.get("company_or_product") or query).strip(),
        "summary": summary,
        "competitors": [
            {
                "name": str(item.get("name", "")).strip(),
                "positioning": str(item.get("positioning", "")).strip(),
                "strengths": str(item.get("strengths", "")).strip(),
                "weaknesses": str(item.get("weaknesses", "")).strip(),
            }
            for item in competitors
            if isinstance(item, dict)
        ],
        "sources": [str(source).strip() for source in sources if str(source).strip()],
    }


def summarize_financial_snapshot(
    query: str,
    company_overview: dict[str, Any],
    chart_data: dict[str, Any],
    system_prompt: str,
    model: str,
) -> str:
    prompt = f"""
{system_prompt}

Write a concise financial analysis reply for the user.
Mention trend direction, one or two notable company facts, and any obvious caveat from the supplied data.
Do not invent data that is not present.

User query: {query}
Company overview: {json.dumps(company_overview)}
Chart data: {json.dumps(chart_data)}
""".strip()
    return generate_text(prompt, model=model) or "I prepared a financial snapshot and chart for this ticker."
