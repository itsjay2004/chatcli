from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class CommandResult:
    handled: bool
    should_exit: bool = False


class CommandHandler:
    def __init__(self, callbacks: dict[str, Callable[[list[str]], CommandResult]]) -> None:
        self.callbacks = callbacks

    def handle(self, text: str) -> CommandResult:
        if not text.startswith("/"):
            return CommandResult(handled=False)

        parts = text.strip().split()
        if not parts:
            return CommandResult(handled=True)

        cmd = parts[0].lower()
        args = parts[1:]

        callback = self.callbacks.get(cmd)
        if callback is None:
            return self.callbacks["/unknown"]([cmd])
        return callback(args)
