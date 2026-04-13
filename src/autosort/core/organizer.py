"""File organization engine for AutoSort."""

from __future__ import annotations

import fnmatch
import logging
import os
import shutil
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class OperationType(Enum):
    MOVE = "move"
    CREATE_DIR = "create_dir"
    DELETE = "delete"


@dataclass
class FileOperation:
    operation_type: OperationType
    source: Path
    destination: Optional[Path] = None
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class FileInfo:
    path: Path
    size: int
    category: str
    subcategory: str = ""
    error_message: str = ""


@dataclass
class OrganizationResult:
    success: bool
    files_processed: int
    files_moved: int
    errors: int
    operations: List[FileOperation]
    error_log: List[str]


class FileOrganizer:
    """Core file organization logic with progress tracking and undo support."""

    def __init__(self, config_manager, path_manager, undo_manager=None):
        self.config_manager = config_manager
        self.path_manager = path_manager
        self.undo_manager = undo_manager
        self.ignore_patterns: List[str] = []
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None
        self.current_transaction_id: Optional[str] = None
        self._extension_map: Optional[Dict[str, str]] = None
        self._categories_cache = None

    def invalidate_cache(self):
        """Clear cached lookups (call after config changes)."""
        self._extension_map = None
        self._categories_cache = None

    @property
    def extension_map(self) -> Dict[str, str]:
        if self._extension_map is None:
            self._extension_map = self.config_manager.get_extension_mapping()
        return self._extension_map

    @property
    def categories(self):
        if self._categories_cache is None:
            self._categories_cache = self.config_manager.get_categories()
        return self._categories_cache

    def set_progress_callback(self, callback: Callable[[int, int, str], None]) -> None:
        self.progress_callback = callback

    def set_current_transaction(self, transaction_id: str) -> None:
        self.current_transaction_id = transaction_id

    def _add_operation_to_transaction(self, operation: FileOperation) -> None:
        if self.undo_manager and self.current_transaction_id:
            self.undo_manager.add_operation(self.current_transaction_id, operation)

    def load_ignore_patterns(self, ignore_file: Path) -> bool:
        try:
            if not ignore_file.exists():
                return True
            with open(ignore_file, "r", encoding="utf-8") as f:
                self.ignore_patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith("#")
                ]
            return True
        except Exception as e:
            logger.error(f"Error loading ignore patterns: {e}")
            return False

    def organize_directory(
        self, source_path: Path, dry_run: bool = False
    ) -> OrganizationResult:
        path_info = self.path_manager.validate_path(source_path)
        if not path_info.exists or not path_info.is_directory:
            return OrganizationResult(
                success=False,
                files_processed=0,
                files_moved=0,
                errors=1,
                operations=[],
                error_log=[f"Invalid source path: {source_path}"],
            )

        target_path = self.path_manager.get_target_path(source_path)
        files = self._scan_files(source_path)
        if not files:
            return OrganizationResult(
                success=True,
                files_processed=0,
                files_moved=0,
                errors=0,
                operations=[],
                error_log=[],
            )
        return self._process_files(files, target_path, dry_run)

    def analyze_files(self, source_path: Path) -> Dict[str, Any]:
        try:
            files = self._scan_files(source_path)
            category_stats: Dict[str, Any] = {}
            total_size = 0
            for fp in files:
                category, subcategory = self._categorize_file(fp)
                size = fp.stat().st_size
                if category not in category_stats:
                    category_stats[category] = {"count": 0, "size": 0, "subcategories": {}}
                category_stats[category]["count"] += 1
                category_stats[category]["size"] += size
                total_size += size
                if subcategory:
                    subs = category_stats[category]["subcategories"]
                    if subcategory not in subs:
                        subs[subcategory] = {"count": 0, "size": 0}
                    subs[subcategory]["count"] += 1
                    subs[subcategory]["size"] += size
            return {"total_files": len(files), "total_size": total_size, "categories": category_stats}
        except Exception as e:
            logger.error(f"Error analyzing files: {e}")
            return {"total_files": 0, "total_size": 0, "categories": {}, "error": str(e)}

    # -- internal helpers --

    def _scan_files(self, source_path: Path) -> List[Path]:
        result = []
        try:
            for item in source_path.iterdir():
                if not item.is_file():
                    continue
                if self._should_skip_file(item):
                    continue
                if self._should_ignore_file(item):
                    continue
                result.append(item)
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
        return result

    _ALWAYS_SKIP = frozenset({
        ".DS_Store", "Thumbs.db", "desktop.ini", ".sortignore",
    })

    def _should_skip_file(self, file_path: Path) -> bool:
        return file_path.name in self._ALWAYS_SKIP

    def _should_ignore_file(self, file_path: Path) -> bool:
        return any(fnmatch.fnmatch(file_path.name, p) for p in self.ignore_patterns)

    def _categorize_file(self, file_path: Path) -> Tuple[str, str]:
        ext = file_path.suffix.lower()
        category = self.extension_map.get(ext, "Miscellaneous")
        subcategory = self._categorize_subcategory(file_path, category)
        return category, subcategory

    def _categorize_subcategory(self, file_path: Path, category_folder_name: str) -> str:
        try:
            category_key = None
            for key, cat in self.categories.items():
                if cat.folder_name == category_folder_name:
                    category_key = key
                    break
            if not category_key:
                return ""
            cat_config = self.categories[category_key]
            if not cat_config.subcategories:
                return ""
            for _name, sub in cat_config.subcategories.items():
                if self._matches_subcategory(file_path, sub):
                    return sub.folder_name
            return ""
        except Exception:
            return ""

    def _matches_subcategory(self, file_path: Path, sub) -> bool:
        ext = file_path.suffix.lower()
        if sub.extensions and ext in [e.lower() for e in sub.extensions]:
            return True
        if sub.patterns:
            for pattern in sub.patterns:
                if fnmatch.fnmatch(file_path.name.lower(), pattern.lower()):
                    return True
        if sub.exif_indicators and self._matches_exif_indicators(file_path, sub.exif_indicators):
            return True
        return False

    def _matches_exif_indicators(self, file_path: Path, indicators: List[str]) -> bool:
        _IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".gif", ".webp"}
        if file_path.suffix.lower() not in _IMAGE_EXTS:
            return False
        try:
            meta = self._read_exif(file_path)
            sw = meta.get("software_used", "") or ""
            cam = meta.get("camera_info", "") or ""
            combined = f"{sw} {cam}".lower()
            return any(ind.lower() in combined for ind in indicators)
        except Exception:
            return False

    def _read_exif(self, file_path: Path) -> Dict[str, Any]:
        meta: Dict[str, Any] = {"software_used": None, "camera_info": None}
        try:
            import PIL.Image
            with PIL.Image.open(file_path) as img:
                exif = img.getexif()
                if exif:
                    meta["software_used"] = exif.get(305)
                    make = exif.get(271)
                    model = exif.get(272)
                    if make or model:
                        meta["camera_info"] = f"{make or ''} {model or ''}".strip()
        except ImportError:
            pass
        except Exception:
            pass
        return meta

    def _process_files(
        self, files: List[Path], target_path: Path, dry_run: bool
    ) -> OrganizationResult:
        operations: List[FileOperation] = []
        error_log: List[str] = []
        files_moved = 0
        errors = 0

        for i, fp in enumerate(files):
            try:
                if self.progress_callback:
                    self.progress_callback(i + 1, len(files), fp.name)
                category, subcategory = self._categorize_file(fp)
                dest_dir = target_path / category / subcategory if subcategory else target_path / category
                if not dry_run and not self.path_manager.ensure_directory(dest_dir):
                    error_log.append(f"Failed to create directory: {dest_dir}")
                    errors += 1
                    continue
                dest_file = self._get_unique_path(dest_dir / fp.name)
                op = FileOperation(operation_type=OperationType.MOVE, source=fp, destination=dest_file)
                if dry_run:
                    operations.append(op)
                else:
                    if self._safe_move_file(fp, dest_file):
                        operations.append(op)
                        self._add_operation_to_transaction(op)
                        files_moved += 1
                    else:
                        error_log.append(f"Failed to move: {fp.name}")
                        errors += 1
            except Exception as e:
                error_log.append(f"Error processing {fp.name}: {e}")
                errors += 1

        return OrganizationResult(
            success=errors == 0,
            files_processed=len(files),
            files_moved=files_moved,
            errors=errors,
            operations=operations,
            error_log=error_log,
        )

    def _get_unique_path(self, dest: Path) -> Path:
        if not dest.exists():
            return dest
        stem, suffix, parent = dest.stem, dest.suffix, dest.parent
        for i in range(1, 1001):
            candidate = parent / f"{stem}_{i}{suffix}"
            if not candidate.exists():
                return candidate
        return parent / f"{stem}_{int(time.time())}{suffix}"

    def _safe_move_file(self, source: Path, dest: Path) -> bool:
        try:
            if not source.exists() or not source.is_file():
                return False
            if not os.access(source, os.R_OK) or not os.access(dest.parent, os.W_OK):
                return False
            shutil.move(str(source), str(dest))
            return True
        except Exception as e:
            logger.error(f"Error moving {source} to {dest}: {e}")
            return False
