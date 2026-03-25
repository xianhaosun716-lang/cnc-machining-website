from __future__ import annotations

import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
DIST = BASE / "dist"
BUILD_OUTPUT_EXE = DIST / "ChatHelper.exe"
RELEASE_ROOT = BASE / "release"
DELIVERABLE_DIR = RELEASE_ROOT / "ChatHelper-Windows"
ZIP_PATH = RELEASE_ROOT / "ChatHelper-Windows.zip"


def write_quickstart(target: Path) -> None:
    content = """Chinese to English Chat Helper - Quick Start
==========================================

1) Double-click ChatHelper.exe to run.
2) Click 设置 (Settings), paste your OpenAI API Key, and save.
3) Press Ctrl+Shift+Space to pop up the app window.
4) Click 开始说话, speak Chinese, then click 停止录音.
5) Click 一键复制英文 and paste into WhatsApp/Facebook/Email.

Notes:
- The app can run without Python installed on user PC.
- History/settings are stored in: %USERPROFILE%\\.cnc_chat_helper
"""
    (target / "QuickStart.txt").write_text(content, encoding="utf-8")


def main() -> None:
    RELEASE_ROOT.mkdir(exist_ok=True)

    if not BUILD_OUTPUT_EXE.exists():
        raise FileNotFoundError(
            "dist/ChatHelper.exe not found. Run PyInstaller first on Windows."
        )

    if DELIVERABLE_DIR.exists():
        shutil.rmtree(DELIVERABLE_DIR)
    DELIVERABLE_DIR.mkdir(parents=True, exist_ok=True)

    shutil.copy2(BUILD_OUTPUT_EXE, DELIVERABLE_DIR / "ChatHelper.exe")
    shutil.copy2(BASE / "README.md", DELIVERABLE_DIR / "README.md")
    if (BASE / "QUICKSTART_GITHUB_CN.md").exists():
        shutil.copy2(BASE / "QUICKSTART_GITHUB_CN.md", DELIVERABLE_DIR / "QUICKSTART_GITHUB_CN.md")
    write_quickstart(DELIVERABLE_DIR)

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    shutil.make_archive(str(ZIP_PATH.with_suffix("")), "zip", DELIVERABLE_DIR)

    print(f"Deliverable folder created: {DELIVERABLE_DIR}")
    print(f"Zip created: {ZIP_PATH}")


if __name__ == "__main__":
    main()
