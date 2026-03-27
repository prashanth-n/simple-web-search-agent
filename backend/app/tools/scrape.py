from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from app.core.llm import post_ollama

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
    )
}


def _truncate(text: str, limit: int) -> str:
    return " ".join(text.split())[:limit]


def _scrape_with_ollama(url: str, limit: int) -> str:
    payload = post_ollama(
        "/web_fetch",
        {"url": url},
        timeout=30,
    )
    return _truncate(str(payload.get("content", "")), limit)


def _scrape_with_requests(url: str, limit: int) -> str:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    return _truncate(soup.get_text(" ", strip=True), limit)


def scrape_page(url: str, limit: int = 5000) -> str:
    try:
        content = _scrape_with_ollama(url, limit)
        if content:
            return content
    except requests.RequestException:
        pass

    return _scrape_with_requests(url, limit)
