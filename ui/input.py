from __future__ import annotations

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings


class ChatInput:
    def __init__(self) -> None:
        self.history = InMemoryHistory()
        self.bindings = KeyBindings()

        @self.bindings.add("c-j")
        def _(event) -> None:  # type: ignore[no-untyped-def]
            event.current_buffer.validate_and_handle()

        self.session = PromptSession(
            history=self.history,
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=self.bindings,
            multiline=True,
        )

    def prompt(self) -> str:
        return self.session.prompt("\n[You] > ")
