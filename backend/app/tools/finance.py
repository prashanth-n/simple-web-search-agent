from __future__ import annotations

from typing import Any

import requests

from app.config import get_settings

ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"


def _alpha_vantage_request(params: dict[str, str]) -> dict[str, Any]:
    settings = get_settings()
    response = requests.get(
        ALPHA_VANTAGE_URL,
        params={**params, "apikey": settings.alpha_vantage_api_key},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if "Error Message" in payload:
        raise ValueError(payload["Error Message"])
    if "Information" in payload:
        raise ValueError(payload["Information"])
    if "Note" in payload:
        raise ValueError(payload["Note"])
    return payload


def get_company_overview(symbol: str) -> dict[str, Any]:
    payload = _alpha_vantage_request({"function": "OVERVIEW", "symbol": symbol})
    if not payload or "Symbol" not in payload:
        raise ValueError(f"No company overview found for ticker {symbol}.")

    return {
        "symbol": payload.get("Symbol", symbol),
        "company": payload.get("Name", symbol),
        "description": payload.get("Description", ""),
        "sector": payload.get("Sector", ""),
        "industry": payload.get("Industry", ""),
        "market_cap": payload.get("MarketCapitalization", ""),
        "pe_ratio": payload.get("PERatio", ""),
        "eps": payload.get("EPS", ""),
        "revenue_ttm": payload.get("RevenueTTM", ""),
        "profit_margin": payload.get("ProfitMargin", ""),
        "beta": payload.get("Beta", ""),
        "website": payload.get("OfficialSite", ""),
        "currency": payload.get("Currency", ""),
        "exchange": payload.get("Exchange", ""),
    }


def get_daily_series(symbol: str, limit: int = 30) -> dict[str, Any]:
    payload = _alpha_vantage_request(
        {"function": "TIME_SERIES_DAILY", "symbol": symbol, "outputsize": "compact"}
    )
    series = payload.get("Time Series (Daily)", {})
    if not series:
        raise ValueError(f"No price series found for ticker {symbol}.")

    points: list[dict[str, Any]] = []
    for date in sorted(series.keys())[-limit:]:
        entry = series[date]
        points.append(
            {
                "date": date,
                "open": float(entry["1. open"]),
                "high": float(entry["2. high"]),
                "low": float(entry["3. low"]),
                "close": float(entry["4. close"]),
                "volume": float(entry["5. volume"]),
            }
        )

    return {"interval": "daily", "points": points}
