from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class HistoryManager:
    def __init__(self, chats_dir: Path | None = None) -> None:
        self.chats_dir = chats_dir or Path("chats")
        self.chats_dir.mkdir(parents=True, exist_ok=True)

    def save_chat(self, title: str | None, messages: list[dict[str, str]]) -> Path:
        timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        payload = {
            "timestamp": timestamp,
            "title": title or self._generate_title(messages),
            "messages": messages,
        }
        file_name = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}.json"
        target = self.chats_dir / file_name
        with target.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        self._prune()
        return target

    def list_chats(self, limit: int = 10) -> list[dict[str, Any]]:
        files = sorted(self.chats_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        entries: list[dict[str, Any]] = []
        for idx, file in enumerate(files[:limit], start=1):
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            entries.append(
                {
                    "id": idx,
                    "file": file,
                    "title": data.get("title", "Untitled"),
                    "timestamp": data.get("timestamp", "Unknown"),
                }
            )
        return entries

    def load_chat_by_id(self, chat_id: int, limit: int = 10) -> dict[str, Any]:
        entries = self.list_chats(limit=limit)
        for entry in entries:
            if entry["id"] == chat_id:
                with entry["file"].open("r", encoding="utf-8") as f:
                    return json.load(f)
        raise ValueError("Chat ID not found.")

    def delete_chat_by_id(self, chat_id: int, limit: int = 10) -> None:
        entries = self.list_chats(limit=limit)
        for entry in entries:
            if entry["id"] == chat_id:
                entry["file"].unlink(missing_ok=True)
                return
        raise ValueError("Chat ID not found.")

    def _prune(self) -> None:
        files = sorted(self.chats_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        if len(files) <= 15:
            return
        # Requirement blend: keep recent chats and prune aggressively once limit is exceeded.
        for old_file in files[10:]:
            old_file.unlink(missing_ok=True)

    @staticmethod
    def _generate_title(messages: list[dict[str, str]]) -> str:
        for msg in messages:
            if msg.get("role") == "user":
                raw = msg.get("content", "").strip().splitlines()[0][:60]
                return raw or "Untitled Chat"
        return "Untitled Chat"
