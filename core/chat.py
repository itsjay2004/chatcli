from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx
from rich.status import Status

from core.commands import CommandHandler, CommandResult
from core.config import ConfigManager
from core.history import HistoryManager
from providers.anthropic_provider import AnthropicProvider
from providers.custom_provider import CustomAnthropicCompatibleProvider, CustomOpenAICompatibleProvider
from providers.google_provider import GoogleProvider
from providers.openai_provider import OpenAIProvider
from providers.openrouter_provider import OpenRouterProvider
from ui.display import ChatDisplay
from ui.input import ChatInput


@dataclass
class ChatState:
    messages: list[dict[str, str]] = field(default_factory=list)
    title: str | None = None


class ChatApplication:
    def __init__(self) -> None:
        self.display = ChatDisplay()
        self.chat_input = ChatInput()
        self.config_manager = ConfigManager()
        self.history_manager = HistoryManager()
        self.state = ChatState()
        self.providers = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "google": GoogleProvider(),
            "openrouter": OpenRouterProvider(),
            "custom_openai": CustomOpenAICompatibleProvider(),
            "custom_anthropic": CustomAnthropicCompatibleProvider(),
        }
        self.command_handler = CommandHandler(
            {
                "/help": self._cmd_help,
                "/clear": self._cmd_clear,
                "/exit": self._cmd_exit,
                "/save": self._cmd_save,
                "/history": self._cmd_history,
                "/load": self._cmd_load,
                "/delete": self._cmd_delete,
                "/config": self._cmd_config,
                "/unknown": self._cmd_unknown,
            }
        )

    def run(self) -> None:
        self.display.banner()
        while True:
            try:
                user_input = self.chat_input.prompt().strip()
            except (EOFError, KeyboardInterrupt):
                self._save_if_needed()
                self.display.show_system("Goodbye!", style="bold green")
                break

            if not user_input:
                self.display.show_system("Please enter a prompt or a command.", style="yellow")
                continue

            result = self.command_handler.handle(user_input)
            if result.handled:
                if result.should_exit:
                    break
                continue

            self._process_chat_turn(user_input)

    def _process_chat_turn(self, user_input: str) -> None:
        self.state.messages.append({"role": "user", "content": user_input})
        self.display.show_user_message(user_input)

        provider_config = self.config_manager.current_provider_config()
        provider_name = provider_config["provider"]
        provider = self.providers.get(provider_name)
        if provider is None:
            self.display.show_error(f"Unsupported provider: {provider_name}")
            return

        try:
            with Status("[bold cyan]Thinking…[/bold cyan]", console=self.display.console, spinner="dots"):
                response = provider.get_response(self.state.messages, provider_config)
        except ValueError as exc:
            self.display.show_error(str(exc))
            return
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:300]
            self.display.show_error(f"API error ({exc.response.status_code}): {detail}")
            return
        except httpx.HTTPError as exc:
            self.display.show_error(f"Network error: {exc}")
            return
        except Exception as exc:  # noqa: BLE001
            self.display.show_error(f"Unexpected error: {exc}")
            return

        self.state.messages.append({"role": "assistant", "content": response})
        self.display.show_assistant_message(response, model_name=provider_config.get("model"))

    def _cmd_help(self, _args: list[str]) -> CommandResult:
        self.display.print_help()
        return CommandResult(handled=True)

    def _cmd_clear(self, _args: list[str]) -> CommandResult:
        self.display.clear_screen()
        self.display.banner()
        self.display.show_system("Screen cleared. Session messages are still in memory.", style="green")
        return CommandResult(handled=True)

    def _cmd_exit(self, _args: list[str]) -> CommandResult:
        self._save_if_needed()
        self.display.show_system("Session saved. Goodbye!", style="bold green")
        return CommandResult(handled=True, should_exit=True)

    def _cmd_save(self, _args: list[str]) -> CommandResult:
        if not self.state.messages:
            self.display.show_system("Nothing to save yet.", style="yellow")
            return CommandResult(handled=True)
        path = self.history_manager.save_chat(self.state.title, self.state.messages)
        self.display.show_system(f"Saved chat to {path}", style="bold green")
        return CommandResult(handled=True)

    def _cmd_history(self, _args: list[str]) -> CommandResult:
        entries = self.history_manager.list_chats(limit=10)
        rows = [(e["id"], e["title"], e["timestamp"]) for e in entries]
        self.display.show_history(rows)
        return CommandResult(handled=True)

    def _cmd_load(self, args: list[str]) -> CommandResult:
        if len(args) != 1 or not args[0].isdigit():
            self.display.show_error("Usage: /load <id>")
            return CommandResult(handled=True)
        chat_id = int(args[0])
        try:
            data = self.history_manager.load_chat_by_id(chat_id, limit=10)
        except ValueError as exc:
            self.display.show_error(str(exc))
            return CommandResult(handled=True)

        self.state.messages = data.get("messages", [])
        self.state.title = data.get("title")
        self.display.show_system(f"Loaded chat #{chat_id}: {self.state.title or 'Untitled'}", style="green")
        for msg in self.state.messages:
            if msg.get("role") == "user":
                self.display.show_user_message(msg.get("content", ""))
            elif msg.get("role") == "assistant":
                self.display.show_assistant_message(msg.get("content", ""))
        return CommandResult(handled=True)

    def _cmd_delete(self, args: list[str]) -> CommandResult:
        if len(args) != 1 or not args[0].isdigit():
            self.display.show_error("Usage: /delete <id>")
            return CommandResult(handled=True)
        chat_id = int(args[0])
        try:
            self.history_manager.delete_chat_by_id(chat_id, limit=10)
        except ValueError as exc:
            self.display.show_error(str(exc))
            return CommandResult(handled=True)
        self.display.show_system(f"Deleted chat #{chat_id}", style="bold green")
        return CommandResult(handled=True)

    def _cmd_config(self, _args: list[str]) -> CommandResult:
        self.config_manager.interactive_config()
        return CommandResult(handled=True)

    def _cmd_unknown(self, args: list[str]) -> CommandResult:
        command = args[0] if args else ""
        self.display.show_error(f"Unknown command: {command}. Use /help.")
        return CommandResult(handled=True)

    def _save_if_needed(self) -> None:
        if self.state.messages:
            self.history_manager.save_chat(self.state.title, self.state.messages)
