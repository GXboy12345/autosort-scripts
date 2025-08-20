"""
Placeholder for removed accessibility/shortcuts functionality.

This module previously contained keyboard shortcuts functionality
that has been removed due to implementation issues.
"""

import logging

logger = logging.getLogger(__name__)


class ShortcutsManager:
    """
    Placeholder shortcuts manager.
    
    This class exists to maintain compatibility with existing code
    but provides no actual functionality.
    """
    
    def __init__(self):
        """Initialize the placeholder shortcuts manager."""
        pass
    
    def register_callback(self, action: str, callback) -> None:
        """Placeholder method - does nothing."""
        pass
    
    def get_shortcuts_info(self) -> dict:
        """Return empty shortcuts info."""
        return {
            "shortcuts_count": 0,
            "shortcuts": [],
            "actions": []
        }


# Backward compatibility alias
AccessibilityManager = ShortcutsManager