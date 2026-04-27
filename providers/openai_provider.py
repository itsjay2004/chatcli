from __future__ import annotations

from typing import Any

import httpx

from providers.base import Provider


class OpenAIProvider(Provider):
    def get_response(self, messages: list[dict[str, str]], config: dict[str, Any]) -> str:
        api_key = config.get("api_key", "")
        if not api_key:
            raise ValueError("Missing API key for OpenAI provider. Update via /config.")

        payload = {
            "model": config.get("model", "gpt-4o-mini"),
            "messages": messages,
            "temperature": config.get("temperature", 0.7),
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        base_url = config.get("base_url", "https://api.openai.com/v1").rstrip("/")

        with httpx.Client(timeout=60) as client:
            response = client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"].strip()
