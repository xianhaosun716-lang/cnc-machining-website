from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

APP_DIR = Path.home() / ".cnc_chat_helper"
SETTINGS_FILE = APP_DIR / "settings.json"
HISTORY_FILE = APP_DIR / "history.json"

DEFAULT_SETTINGS: Dict[str, Any] = {
    "hotkey": "ctrl+shift+space",
    "translation_style": "business",
    "always_on_top": True,
    "auto_copy_english": False,
    "history_limit": 20,
    "sample_rate": 16000,
    "startup_launch": False,
    "openai_api_key": "",
    "openai_transcribe_model": "gpt-4o-mini-transcribe",
    "openai_translate_model": "gpt-4.1-mini",
}


def ensure_app_dir() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)


def load_settings() -> Dict[str, Any]:
    ensure_app_dir()
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS.copy())
        return DEFAULT_SETTINGS.copy()

    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        data = {}

    merged = DEFAULT_SETTINGS.copy()
    merged.update(data)

    # Simple value guards to avoid crash from manual edits.
    if not isinstance(merged.get("history_limit"), int):
        merged["history_limit"] = DEFAULT_SETTINGS["history_limit"]
    merged["history_limit"] = max(5, min(200, merged["history_limit"]))

    if not isinstance(merged.get("sample_rate"), int):
        merged["sample_rate"] = DEFAULT_SETTINGS["sample_rate"]

    return merged


def save_settings(settings: Dict[str, Any]) -> None:
    ensure_app_dir()
    SETTINGS_FILE.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8"
    )
