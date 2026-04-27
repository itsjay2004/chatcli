from __future__ import annotations

from typing import Any

import httpx

from providers.base import Provider


class GoogleProvider(Provider):
    def get_response(self, messages: list[dict[str, str]], config: dict[str, Any]) -> str:
        api_key = config.get("api_key", "")
        if not api_key:
            raise ValueError("Missing API key for Google provider. Update via /config.")

        model = config.get("model", "gemini-1.5-flash")
        base_url = config.get("base_url", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")

        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": config.get("temperature", 0.7),
            },
        }

        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{base_url}/models/{model}:generateContent",
                params={"key": api_key},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts).strip()
