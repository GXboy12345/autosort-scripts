"""macOS Notification Center integration via osascript."""

from __future__ import annotations

import logging
import subprocess
from typing import Dict

logger = logging.getLogger(__name__)


def notify(title: str, message: str, sound: bool = False) -> None:
    """Post a notification to macOS Notification Center."""
    safe_title = title.replace('"', '\\"')
    safe_msg = message.replace('"', '\\"')
    script = f'display notification "{safe_msg}" with title "{safe_title}"'
    if sound:
        script += ' sound name "Pop"'
    try:
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            timeout=5,
        )
    except Exception as e:
        logger.debug(f"Notification failed: {e}")


def notify_sort_complete(results: Dict[str, int], quiet: bool = False) -> None:
    """Send a summary notification after sorting completes."""
    if quiet:
        return
    total = sum(results.values())
    if total == 0:
        return
    parts = [f"{count} to {cat}" for cat, count in sorted(results.items(), key=lambda x: -x[1])[:4]]
    summary = ", ".join(parts)
    if len(results) > 4:
        summary += f" (+{len(results) - 4} more)"
    notify("AutoSort", f"Moved {total} files: {summary}")
