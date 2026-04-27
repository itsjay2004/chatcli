from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Provider(ABC):
    @abstractmethod
    def get_response(self, messages: list[dict[str, str]], config: dict[str, Any]) -> str:
        raise NotImplementedError
