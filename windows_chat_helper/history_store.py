from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List

from config import HISTORY_FILE, ensure_app_dir


class HistoryStore:
    def __init__(self, limit: int = 20) -> None:
        self.limit = limit
        ensure_app_dir()

    def load(self) -> List[Dict[str, str]]:
        if not HISTORY_FILE.exists():
            return []

        try:
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except (OSError, json.JSONDecodeError):
            return []
        return []

    def add(self, chinese: str, english: str) -> None:
        items = self.load()
        items.insert(
            0,
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "chinese": chinese,
                "english": english,
            },
        )
        items = items[: self.limit]
        HISTORY_FILE.write_text(
            json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def clear(self) -> None:
        HISTORY_FILE.write_text("[]", encoding="utf-8")
