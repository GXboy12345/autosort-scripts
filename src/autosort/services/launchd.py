"""macOS LaunchAgent management for AutoSort watch mode."""

from __future__ import annotations

import logging
import plistlib
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

LABEL = "com.autosort.watcher"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def _find_autosort_bin() -> str:
    """Locate the autosort binary on PATH."""
    which = shutil.which("autosort")
    return which or "autosort"


def install(watch_paths: list[str], quiet: bool = True) -> Path:
    """Generate and load a LaunchAgent plist for autosort watch."""
    args = [_find_autosort_bin(), "watch"]
    for p in watch_paths:
        args.append(p)
    if quiet:
        args.append("--quiet")

    plist = {
        "Label": LABEL,
        "ProgramArguments": args,
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": str(Path.home() / "Library" / "Logs" / "autosort.log"),
        "StandardErrorPath": str(Path.home() / "Library" / "Logs" / "autosort.err"),
    }

    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PLIST_PATH, "wb") as f:
        plistlib.dump(plist, f)

    subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
    subprocess.run(["launchctl", "load", str(PLIST_PATH)], check=True, capture_output=True)
    return PLIST_PATH


def uninstall() -> bool:
    """Unload and remove the LaunchAgent plist."""
    if not PLIST_PATH.exists():
        return False
    subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
    PLIST_PATH.unlink(missing_ok=True)
    return True


def is_installed() -> bool:
    return PLIST_PATH.exists()


def status() -> str:
    """Check if the LaunchAgent is currently loaded."""
    if not PLIST_PATH.exists():
        return "not installed"
    result = subprocess.run(
        ["launchctl", "list", LABEL],
        capture_output=True,
        text=True,
    )
    return "running" if result.returncode == 0 else "installed but not running"
