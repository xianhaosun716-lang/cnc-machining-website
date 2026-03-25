from __future__ import annotations

import sys
from pathlib import Path


def is_windows() -> bool:
    return sys.platform.startswith("win")


def set_startup(enabled: bool) -> None:
    """Add/remove app startup registration in HKCU Run.

    Works when running packaged exe. For script mode, it points to python + app.py path.
    """
    if not is_windows():
        return

    import winreg  # pylint: disable=import-outside-toplevel

    app_name = "CNCChatHelper"
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE,
    )

    if enabled:
        if getattr(sys, "frozen", False):
            cmd = f'"{Path(sys.executable)}"'
        else:
            script_path = Path(__file__).resolve().parent / "app.py"
            cmd = f'"{Path(sys.executable)}" "{script_path}"'
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
    else:
        try:
            winreg.DeleteValue(key, app_name)
        except FileNotFoundError:
            pass

    winreg.CloseKey(key)
