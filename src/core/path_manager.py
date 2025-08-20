"""
Path Manager for AutoSort

Handles path detection, validation, and folder selection with improved
error handling and cross-platform support.
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PathType(Enum):
    """Path type enumeration."""
    DESKTOP = "desktop"
    DOWNLOADS = "downloads"
    CUSTOM = "custom"
    INVALID = "invalid"


@dataclass
class PathInfo:
    """Path information structure."""
    path: Path
    path_type: PathType
    exists: bool
    is_directory: bool
    is_writable: bool
    error_message: str = ""


class PathManager:
    """
    Manages path detection, validation, and folder selection.
    
    This class handles finding common directories like Desktop and Downloads,
    validating paths, and providing folder selection dialogs with proper
    error handling and cross-platform support.
    """
    
    def __init__(self):
        """Initialize the path manager."""
        self._desktop_path: Optional[Path] = None
        self._downloads_path: Optional[Path] = None
    
    def get_desktop_path(self) -> Path:
        """
        Get the Desktop path, handling different locales.
        
        Returns:
            Path to Desktop directory
        """
        if self._desktop_path is None:
            self._desktop_path = self._detect_desktop_path()
        
        return self._desktop_path
    
    def get_downloads_path(self) -> Path:
        """
        Get the Downloads path, handling different locales.
        
        Returns:
            Path to Downloads directory
        """
        if self._downloads_path is None:
            self._downloads_path = self._detect_downloads_path()
        
        return self._downloads_path
    
    def validate_path(self, path: Path) -> PathInfo:
        """
        Validate a path and return detailed information.
        
        Args:
            path: Path to validate
            
        Returns:
            PathInfo object with validation results
        """
        try:
            exists = path.exists()
            is_directory = path.is_dir() if exists else False
            is_writable = self._check_writable(path) if exists else False
            
            # Determine path type
            path_type = self._determine_path_type(path)
            
            return PathInfo(
                path=path,
                path_type=path_type,
                exists=exists,
                is_directory=is_directory,
                is_writable=is_writable
            )
            
        except Exception as e:
            logger.error(f"Error validating path {path}: {e}")
            return PathInfo(
                path=path,
                path_type=PathType.INVALID,
                exists=False,
                is_directory=False,
                is_writable=False,
                error_message=str(e)
            )
    
    def select_folder_dialog(self, title: str = "Select folder to organize") -> Optional[Path]:
        """
        Open a folder selection dialog.
        
        Args:
            title: Dialog title
            
        Returns:
            Selected path or None if cancelled/error
        """
        try:
            if self._is_macos():
                return self._macos_folder_dialog(title)
            elif self._is_windows():
                return self._windows_folder_dialog(title)
            else:
                return self._linux_folder_dialog(title)
                
        except Exception as e:
            logger.error(f"Error opening folder dialog: {e}")
            return None
    
    def get_target_path(self, source_path: Path) -> Path:
        """
        Get the target path for organizing files.
        
        Args:
            source_path: Source directory path
            
        Returns:
            Target directory path
        """
        return source_path / "Autosort"
    
    def ensure_directory(self, path: Path) -> bool:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            path: Directory path to create
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating directory {path}: {e}")
            return False
    
    def _detect_desktop_path(self) -> Path:
        """
        Detect Desktop path for different locales.
        
        Returns:
            Desktop path
        """
        # Common Desktop folder names in different languages
        desktop_names = [
            "Desktop",
            "Escritorio",  # Spanish
            "Bureau",       # French
            "Schreibtisch", # German
            "Desktop"       # Fallback
        ]
        
        home = Path.home()
        
        for name in desktop_names:
            path = home / name
            if path.exists() and path.is_dir():
                logger.debug(f"Found Desktop at: {path}")
                return path
        
        # Fallback to standard Desktop path
        fallback_path = home / "Desktop"
        logger.warning(f"Desktop not found, using fallback: {fallback_path}")
        return fallback_path
    
    def _detect_downloads_path(self) -> Path:
        """
        Detect Downloads path for different locales.
        
        Returns:
            Downloads path
        """
        # Common Downloads folder names in different languages
        downloads_names = [
            "Downloads",
            "Descargas",        # Spanish
            "Téléchargements",  # French
            "Downloads"         # Fallback
        ]
        
        home = Path.home()
        
        for name in downloads_names:
            path = home / name
            if path.exists() and path.is_dir():
                logger.debug(f"Found Downloads at: {path}")
                return path
        
        # Fallback to standard Downloads path
        fallback_path = home / "Downloads"
        logger.warning(f"Downloads not found, using fallback: {fallback_path}")
        return fallback_path
    
    def _check_writable(self, path: Path) -> bool:
        """
        Check if a path is writable.
        
        Args:
            path: Path to check
            
        Returns:
            True if writable, False otherwise
        """
        try:
            # Try to create a temporary file to test write access
            test_file = path / ".autosort_test"
            test_file.touch()
            test_file.unlink()
            return True
            
        except Exception:
            return False
    
    def _determine_path_type(self, path: Path) -> PathType:
        """
        Determine the type of a path.
        
        Args:
            path: Path to analyze
            
        Returns:
            PathType enumeration
        """
        try:
            # Resolve to absolute path for comparison
            resolved_path = path.resolve()
            
            # Check if it's Desktop
            desktop_path = self.get_desktop_path().resolve()
            if resolved_path == desktop_path:
                return PathType.DESKTOP
            
            # Check if it's Downloads
            downloads_path = self.get_downloads_path().resolve()
            if resolved_path == downloads_path:
                return PathType.DOWNLOADS
            
            # Must be custom
            return PathType.CUSTOM
            
        except Exception:
            return PathType.INVALID
    
    def _is_macos(self) -> bool:
        """Check if running on macOS."""
        import platform
        return platform.system() == "Darwin"
    
    def _is_windows(self) -> bool:
        """Check if running on Windows."""
        import platform
        return platform.system() == "Windows"
    
    def _macos_folder_dialog(self, title: str) -> Optional[Path]:
        """
        Open folder selection dialog on macOS.
        
        Args:
            title: Dialog title
            
        Returns:
            Selected path or None
        """
        try:
            script = f'''
            tell application "System Events"
                activate
                set folderPath to choose folder with prompt "{title}"
                return POSIX path of folderPath
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                selected_path = Path(result.stdout.strip())
                logger.debug(f"Selected folder: {selected_path}")
                return selected_path
            else:
                logger.debug("Folder selection was cancelled")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Folder selection dialog timed out")
            return None
        except Exception as e:
            logger.error(f"Error in macOS folder dialog: {e}")
            return None
    
    def _windows_folder_dialog(self, title: str) -> Optional[Path]:
        """
        Open folder selection dialog on Windows.
        
        Args:
            title: Dialog title
            
        Returns:
            Selected path or None
        """
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            # Create a hidden root window
            root = tk.Tk()
            root.withdraw()
            
            # Open folder dialog
            folder_path = filedialog.askdirectory(title=title)
            
            # Destroy the root window
            root.destroy()
            
            if folder_path:
                selected_path = Path(folder_path)
                logger.debug(f"Selected folder: {selected_path}")
                return selected_path
            else:
                logger.debug("Folder selection was cancelled")
                return None
                
        except Exception as e:
            logger.error(f"Error in Windows folder dialog: {e}")
            return None
    
    def _linux_folder_dialog(self, title: str) -> Optional[Path]:
        """
        Open folder selection dialog on Linux.
        
        Args:
            title: Dialog title
            
        Returns:
            Selected path or None
        """
        try:
            # Try zenity first
            result = subprocess.run(
                ['zenity', '--file-selection', '--directory', '--title', title],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                selected_path = Path(result.stdout.strip())
                logger.debug(f"Selected folder: {selected_path}")
                return selected_path
            
            # Fallback to tkinter
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            
            folder_path = filedialog.askdirectory(title=title)
            root.destroy()
            
            if folder_path:
                selected_path = Path(folder_path)
                logger.debug(f"Selected folder: {selected_path}")
                return selected_path
            else:
                logger.debug("Folder selection was cancelled")
                return None
                
        except Exception as e:
            logger.error(f"Error in Linux folder dialog: {e}")
            return None
