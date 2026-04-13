"""Path detection and validation for macOS."""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PathType(Enum):
    DESKTOP = "desktop"
    DOWNLOADS = "downloads"
    CUSTOM = "custom"
    INVALID = "invalid"


@dataclass
class PathInfo:
    path: Path
    path_type: PathType
    exists: bool
    is_directory: bool
    is_writable: bool
    error_message: str = ""


class PathManager:
    """Detects, validates, and selects paths on macOS."""

    def __init__(self):
        self._desktop: Optional[Path] = None
        self._downloads: Optional[Path] = None

    def get_desktop_path(self) -> Path:
        if self._desktop is None:
            self._desktop = self._detect_path(
                ["Desktop", "Escritorio", "Bureau", "Schreibtisch"]
            )
        return self._desktop

    def get_downloads_path(self) -> Path:
        if self._downloads is None:
            self._downloads = self._detect_path(
                ["Downloads", "Descargas", "Téléchargements"]
            )
        return self._downloads

    def validate_path(self, path: Path) -> PathInfo:
        try:
            exists = path.exists()
            is_dir = path.is_dir() if exists else False
            writable = self._check_writable(path) if exists and is_dir else False
            return PathInfo(
                path=path,
                path_type=self._classify(path),
                exists=exists,
                is_directory=is_dir,
                is_writable=writable,
            )
        except Exception as e:
            return PathInfo(
                path=path,
                path_type=PathType.INVALID,
                exists=False,
                is_directory=False,
                is_writable=False,
                error_message=str(e),
            )

    def select_folder_dialog(self, title: str = "Select folder to organize") -> Optional[Path]:
        safe_title = title.replace("\\", "\\\\").replace('"', '\\"')
        script = (
            'tell application "System Events"\n'
            "  activate\n"
            f'  set folderPath to choose folder with prompt "{safe_title}"\n'
            "  return POSIX path of folderPath\n"
            "end tell"
        )
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0 and result.stdout.strip():
                return Path(result.stdout.strip())
            return None
        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            logger.error(f"Folder dialog error: {e}")
            return None

    def get_target_path(self, source_path: Path) -> Path:
        return source_path / "Autosort"

    def ensure_directory(self, path: Path) -> bool:
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Cannot create directory {path}: {e}")
            return False

    def _detect_path(self, candidates: list[str]) -> Path:
        home = Path.home()
        for name in candidates:
            p = home / name
            if p.is_dir():
                return p
        return home / candidates[0]

    def _check_writable(self, path: Path) -> bool:
        probe = path / ".autosort_probe"
        try:
            probe.touch()
            probe.unlink()
            return True
        except Exception:
            return False

    def _classify(self, path: Path) -> PathType:
        try:
            resolved = path.resolve()
            if resolved == self.get_desktop_path().resolve():
                return PathType.DESKTOP
            if resolved == self.get_downloads_path().resolve():
                return PathType.DOWNLOADS
            return PathType.CUSTOM
        except Exception:
            return PathType.INVALID
