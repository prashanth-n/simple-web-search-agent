from __future__ import annotations

from typing import Any

import requests

from app.config import get_settings


def _ollama_headers() -> dict[str, str]:
    settings = get_settings()
    return {
        "Authorization": f"Bearer {settings.ollama_api_key}",
        "Content-Type": "application/json",
    }


def post_ollama(path: str, payload: dict[str, Any], timeout: int = 90) -> dict[str, Any]:
    settings = get_settings()
    response = requests.post(
        f"{settings.ollama_base_url.rstrip('/')}/{path.lstrip('/')}",
        headers=_ollama_headers(),
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def _generate(prompt: str, model: str | None, response_format: str | None = None) -> str:
    settings = get_settings()
    payload: dict[str, Any] = {
        "model": model or settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    if response_format:
        payload["format"] = response_format

    response = post_ollama("/generate", payload)
    return response.get("response", "")


def generate_json(prompt: str, model: str | None = None) -> str:
    return _generate(prompt, model, response_format="json") or "{}"


def generate_text(prompt: str, model: str | None = None) -> str:
    return _generate(prompt, model).strip()
