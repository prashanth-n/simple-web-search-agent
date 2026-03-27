from __future__ import annotations

import json

from app.core.llm import generate_json


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
