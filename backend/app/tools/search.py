from __future__ import annotations

from typing import TypedDict
from urllib.parse import parse_qs, unquote, urlparse

import requests
from bs4 import BeautifulSoup

SEARCH_URL = "https://html.duckduckgo.com/html/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
    )
}


class SearchResult(TypedDict):
    title: str
    link: str


def _normalize_link(raw_link: str) -> str:
    parsed = urlparse(raw_link)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        redirect = parse_qs(parsed.query).get("uddg", [])
        if redirect:
            return unquote(redirect[0])
    return raw_link


def search_web(query: str, limit: int = 5) -> list[SearchResult]:
    response = requests.get(
        SEARCH_URL,
        params={"q": query},
        headers=HEADERS,
        timeout=20,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results: list[SearchResult] = []

    for link in soup.select("a.result__a"):
        title = " ".join(link.get_text(" ", strip=True).split())
        href = _normalize_link(link.get("href", "").strip())
        if not title or not href:
            continue

        results.append({"title": title, "link": href})
        if len(results) >= limit:
            break

    if results:
        return results

    for link in soup.select("a[href]"):
        href = _normalize_link(link.get("href", "").strip())
        title = " ".join(link.get_text(" ", strip=True).split())
        if href.startswith("http") and title:
            results.append({"title": title, "link": href})
            if len(results) >= limit:
                break

    return results
