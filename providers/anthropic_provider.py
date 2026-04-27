from __future__ import annotations

from typing import Any

import httpx

from providers.base import Provider


class AnthropicProvider(Provider):
    def get_response(self, messages: list[dict[str, str]], config: dict[str, Any]) -> str:
        api_key = config.get("api_key", "")
        if not api_key:
            raise ValueError("Missing API key for Anthropic provider. Update via /config.")

        anthropic_messages = [m for m in messages if m["role"] in {"user", "assistant"}]
        payload = {
            "model": config.get("model", "claude-3-5-sonnet-latest"),
            "messages": anthropic_messages,
            "max_tokens": 2048,
            "temperature": config.get("temperature", 0.7),
        }
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        base_url = config.get("base_url", "https://api.anthropic.com/v1").rstrip("/")

        with httpx.Client(timeout=60) as client:
            response = client.post(f"{base_url}/messages", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content_chunks = data.get("content", [])
        text = "".join(chunk.get("text", "") for chunk in content_chunks if chunk.get("type") == "text")
        return text.strip()
