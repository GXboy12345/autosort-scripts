#!/usr/bin/env python3
"""
AutoSort - File Organizer with Enhanced UX

A modern file organization tool with improved user experience, code clarity,
and maintainability. Features include better error handling, accessibility,
undo functionality, and modular architecture.

Requirements:
- Python 3.8+
- macOS (for Desktop path detection and folder dialog)

Copyright (c) 2024 Gboy
Licensed under the MIT License - see LICENSE file for details.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Add the src directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config_manager import ConfigManager
from core.file_organizer import FileOrganizer
from core.path_manager import PathManager
from ui.cli_interface import CLIInterface
from ui.gui_interface import GUIInterface
from utils.logger import setup_logging

from utils.undo_manager import UndoManager

class AutoSortApp:
    """
    Main application class that orchestrates the file organization process.
    
    This class provides a clean interface for the AutoSort application,
    handling initialization, configuration, and the main application flow.
    """
    
    def __init__(self, use_gui: bool = False):
        """
        Initialize the AutoSort application.
        
        Args:
            use_gui: Whether to use the GUI interface (default: False)
        """
        self.use_gui = use_gui
        self.logger = setup_logging()
        
        # Initialize core components
        self.config_manager = ConfigManager()
        self.path_manager = PathManager()
        self.undo_manager = UndoManager()
        self.file_organizer = FileOrganizer(self.config_manager, self.path_manager, self.undo_manager)
        
        # Initialize UI
        if use_gui:
            self.interface = GUIInterface(
                self.config_manager,
                self.file_organizer,
                self.undo_manager
            )
        else:
            self.interface = CLIInterface(
                self.config_manager,
                self.file_organizer,
                self.undo_manager
            )
    
    def run(self) -> int:
        """
        Run the AutoSort application.
        
        Returns:
            Exit code (0 for success, non-zero for errors)
        """
        try:
            self.logger.info("Starting AutoSort application")
            
            # Initialize configuration
            if not self.config_manager.load_config():
                self.logger.error("Failed to load configuration")
                return 1
            
            # Check dependencies
            if not self._check_dependencies():
                self.logger.error("Missing required dependencies")
                return 1
            
            # Run the interface
            return self.interface.run()
            
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            return 0
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return 1
        finally:
            self.logger.info("AutoSort application finished")
    
    def _check_dependencies(self) -> bool:
        """
        Check if all required dependencies are available.
        
        Returns:
            True if all dependencies are available, False otherwise
        """
        try:
            # Check for Pillow (required for image metadata)
            import PIL
            self.logger.debug("Pillow is available for image metadata analysis")
        except ImportError:
            self.logger.warning("Pillow not available - image metadata analysis will be disabled")
        
        # Check for tkinter if using GUI
        if self.use_gui:
            try:
                import tkinter
                self.logger.debug("tkinter is available for GUI")
            except ImportError:
                self.logger.error("tkinter not available - GUI cannot be used")
                return False
        
        return True


def main():
    """
    Main entry point for the AutoSort application.
    
    Determines whether to use GUI or CLI based on command line arguments
    and runs the appropriate interface.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AutoSort - File Organizer with Enhanced UX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python autosort.py          # Use CLI interface
  python autosort.py --gui    # Use GUI interface
  python autosort.py --help   # Show this help message
        """
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Use graphical user interface instead of command line'
    )
    

    
    args = parser.parse_args()
    

    
    # Create and run the application
    app = AutoSortApp(use_gui=args.gui)
    exit_code = app.run()
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
