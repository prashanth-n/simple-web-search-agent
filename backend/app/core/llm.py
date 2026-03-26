from __future__ import annotations

import requests

from app.config import get_settings


def generate_json(prompt: str) -> str:
    settings = get_settings()
    response = requests.post(
        f"{settings.ollama_base_url.rstrip('/')}/generate",
        headers={
            "Authorization": f"Bearer {settings.ollama_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=90,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("response", "{}")
