from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.prompt import FloatPrompt, Prompt


class ConfigManager:
    DEFAULT_CONFIG = {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "providers": {
            "openai": {"api_key": "", "base_url": "https://api.openai.com/v1"},
            "anthropic": {"api_key": "", "base_url": "https://api.anthropic.com/v1"},
            "google": {"api_key": "", "base_url": "https://generativelanguage.googleapis.com/v1beta"},
            "openrouter": {"api_key": "", "base_url": "https://openrouter.ai/api/v1"},
            "custom_openai": {"api_key": "", "base_url": "https://api.openai.com/v1"},
            "custom_anthropic": {"api_key": "", "base_url": "https://api.anthropic.com/v1"},
        },
    }

    PROVIDER_CHOICES = [
        "openai",
        "anthropic",
        "google",
        "openrouter",
        "custom_openai",
        "custom_anthropic",
    ]

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or Path.home() / ".config.json"
        self.console = Console()
        self.config = self.load()

    def load(self) -> dict[str, Any]:
        if not self.config_path.exists():
            self.save(self.DEFAULT_CONFIG)
            return json.loads(json.dumps(self.DEFAULT_CONFIG))
        with self.config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return self._merged(data)

    def _merged(self, loaded: dict[str, Any]) -> dict[str, Any]:
        merged = json.loads(json.dumps(self.DEFAULT_CONFIG))
        merged.update({k: v for k, v in loaded.items() if k != "providers"})
        loaded_providers = loaded.get("providers", {})
        for name, default_provider in merged["providers"].items():
            if name in loaded_providers:
                default_provider.update(loaded_providers[name])
        return merged

    def save(self, data: dict[str, Any] | None = None) -> None:
        to_save = data or self.config
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=2)

    def current_provider_config(self) -> dict[str, Any]:
        provider = self.config.get("provider", "openai")
        provider_conf = self.config["providers"].get(provider, {})
        return {
            "provider": provider,
            "model": self.config.get("model"),
            "temperature": self.config.get("temperature", 0.7),
            "api_key": provider_conf.get("api_key", ""),
            "base_url": provider_conf.get("base_url", ""),
        }

    def interactive_config(self) -> None:
        self.console.print("\n[bold cyan]Configuration[/bold cyan]")
        current_provider = self.config.get("provider", "openai")
        provider = Prompt.ask(
            "Provider",
            choices=self.PROVIDER_CHOICES,
            default=current_provider,
            show_choices=True,
        )
        self.config["provider"] = provider

        model_default = self.config.get("model") or self._default_model(provider)
        self.config["model"] = Prompt.ask("Model", default=model_default)

        temp_default = float(self.config.get("temperature", 0.7))
        self.config["temperature"] = FloatPrompt.ask("Temperature", default=temp_default)

        provider_block = self.config["providers"][provider]
        provider_block["api_key"] = Prompt.ask(
            f"API key for {provider}",
            default=provider_block.get("api_key", ""),
            password=True,
        )

        base_default = provider_block.get("base_url") or self._default_base_url(provider)
        provider_block["base_url"] = Prompt.ask("Base URL", default=base_default)

        self.save()
        self.console.print("[bold green]Configuration updated.[/bold green]")

    @staticmethod
    def _default_model(provider: str) -> str:
        defaults = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-5-sonnet-latest",
            "google": "gemini-1.5-flash",
            "openrouter": "openai/gpt-4o-mini",
            "custom_openai": "gpt-4o-mini",
            "custom_anthropic": "claude-3-5-sonnet-latest",
        }
        return defaults.get(provider, "gpt-4o-mini")

    @staticmethod
    def _default_base_url(provider: str) -> str:
        defaults = {
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com/v1",
            "google": "https://generativelanguage.googleapis.com/v1beta",
            "openrouter": "https://openrouter.ai/api/v1",
            "custom_openai": "https://api.openai.com/v1",
            "custom_anthropic": "https://api.anthropic.com/v1",
        }
        return defaults.get(provider, "")
