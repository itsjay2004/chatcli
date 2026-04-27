from __future__ import annotations

from typing import Any

from providers.anthropic_provider import AnthropicProvider
from providers.openai_provider import OpenAIProvider


class CustomOpenAICompatibleProvider(OpenAIProvider):
    def get_response(self, messages: list[dict[str, str]], config: dict[str, Any]) -> str:
        return super().get_response(messages, config)


class CustomAnthropicCompatibleProvider(AnthropicProvider):
    def get_response(self, messages: list[dict[str, str]], config: dict[str, Any]) -> str:
        return super().get_response(messages, config)
