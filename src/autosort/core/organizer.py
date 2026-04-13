"""File organization engine for AutoSort."""

from __future__ import annotations

import fnmatch
import logging
import os
import re
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from autosort.core.config import Category, MatchCondition, SortRule

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
    rule_folder: str = ""
    rule_name: str = ""
    error_message: str = ""


@dataclass
class OrganizationResult:
    success: bool
    files_processed: int
    files_moved: int
    errors: int
    operations: List[FileOperation]
    error_log: List[str]


class _FileSignals:
    """Per-file cached stat and EXIF for rule evaluation."""

    __slots__ = ("_path", "_stat", "_exif", "_stat_err", "_exif_done")

    def __init__(self, path: Path):
        self._path = path
        self._stat: Optional[os.stat_result] = None
        self._stat_err: Optional[Exception] = None
        self._exif: Dict[str, Any] = {}
        self._exif_done = False

    def stat(self) -> Optional[os.stat_result]:
        if self._stat_err is not None:
            return None
        if self._stat is None:
            try:
                self._stat = self._path.stat()
            except OSError as e:
                self._stat_err = e
                return None
        return self._stat

    def exif(self) -> Dict[str, Any]:
        if not self._exif_done:
            self._exif = _read_exif(self._path)
            self._exif_done = True
        return self._exif


def _read_exif(file_path: Path) -> Dict[str, Any]:
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


_EXIF_IMAGE_SUFFIXES = frozenset(
    {
        ".jpg",
        ".jpeg",
        ".png",
        ".tiff",
        ".tif",
        ".bmp",
        ".gif",
        ".webp",
        ".heic",
        ".heif",
        ".avif",
        ".jxl",
    }
)


def _exif_combined_string(file_path: Path, sig: _FileSignals) -> str:
    if file_path.suffix.lower() not in _EXIF_IMAGE_SUFFIXES:
        return ""
    m = sig.exif()
    sw = m.get("software_used") or ""
    cam = m.get("camera_info") or ""
    return f"{sw} {cam}".lower()


def _looks_like_screenshot_software(sw: str) -> bool:
    if not sw:
        return False
    s = str(sw).lower()
    keys = (
        "screenshot",
        "screen shot",
        "snipping",
        "snagit",
        "cleanshot",
        "shottr",
        "gyazo",
        "lightshot",
        "skitch",
        "screencapture",
        "kap",
    )
    return any(k in s for k in keys)


def _parse_iso_date(s: str) -> Optional[float]:
    try:
        raw = str(s).strip()
        if not raw:
            return None
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except Exception:
        return None


def _check_condition(
    file_path: Path,
    cond: MatchCondition,
    sig: _FileSignals,
) -> bool:
    ct = cond.type
    ext = file_path.suffix.lower()
    name = file_path.name

    if ct == "extension":
        vals = cond.values or ([] if cond.value is None else [cond.value])
        want = {str(v).lower() if str(v).startswith(".") else f".{str(v).lower().lstrip('.')}" for v in vals}
        return ext in want

    if ct == "glob":
        vals = cond.values or ([] if cond.value is None else [cond.value])
        nl = name.lower()
        for pat in vals:
            if fnmatch.fnmatch(nl, str(pat).lower()):
                return True
        return False

    if ct == "regex":
        pat = cond.value if cond.value is not None else (cond.values[0] if cond.values else None)
        if not pat:
            return False
        try:
            return re.search(str(pat), name, re.IGNORECASE) is not None
        except re.error:
            logger.debug("Invalid regex in rule: %s", pat)
            return False

    if ct == "exif_contains":
        combined = _exif_combined_string(file_path, sig)
        if not combined:
            return False
        for v in cond.values or ([] if cond.value is None else [cond.value]):
            if str(v).lower() in combined:
                return True
        return False

    if ct == "exif_camera":
        if file_path.suffix.lower() not in _EXIF_IMAGE_SUFFIXES:
            return False
        cam = (sig.exif().get("camera_info") or "").strip()
        return bool(cam)

    if ct == "exif_screenshot_like":
        if file_path.suffix.lower() not in _EXIF_IMAGE_SUFFIXES:
            return False
        sw = sig.exif().get("software_used") or ""
        return _looks_like_screenshot_software(str(sw))

    st = sig.stat()
    if st is None:
        return False

    if ct == "size_gte":
        lim = cond.value if cond.value is not None else (cond.values[0] if cond.values else None)
        if lim is None:
            return False
        try:
            return st.st_size >= int(lim)
        except (TypeError, ValueError):
            return False

    if ct == "size_lte":
        lim = cond.value if cond.value is not None else (cond.values[0] if cond.values else None)
        if lim is None:
            return False
        try:
            return st.st_size <= int(lim)
        except (TypeError, ValueError):
            return False

    birth = getattr(st, "st_birthtime", None)
    ts = float(birth) if birth not in (None, 0) else float(st.st_mtime)

    if ct == "created_after":
        lim = _parse_iso_date(str(cond.value if cond.value is not None else ""))
        if lim is None and cond.values:
            lim = _parse_iso_date(str(cond.values[0]))
        return lim is not None and ts >= lim

    if ct == "created_before":
        lim = _parse_iso_date(str(cond.value if cond.value is not None else ""))
        if lim is None and cond.values:
            lim = _parse_iso_date(str(cond.values[0]))
        return lim is not None and ts <= lim

    logger.warning("Unknown rule condition type: %s", ct)
    return False


def _rule_matches(file_path: Path, rule: SortRule, sig: _FileSignals) -> bool:
    if not rule.conditions:
        return False
    mode = rule.match_mode if rule.match_mode in ("all", "any") else "all"
    if mode == "all":
        return all(_check_condition(file_path, c, sig) for c in rule.conditions)
    return any(_check_condition(file_path, c, sig) for c in rule.conditions)


def _evaluate_rules_for_category(file_path: Path, cat: Category) -> Tuple[str, str]:
    """Return ``(rule_folder, rule_name)`` for the first matching rule, else ``("", "")``."""
    if not cat.rules:
        return "", ""
    sig = _FileSignals(file_path)
    for rule in cat.rules:
        if _rule_matches(file_path, rule, sig):
            return rule.folder.strip("/").replace("\\", "/"), rule.name
    return "", ""


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

    def resort_directory(
        self, source_path: Path, dry_run: bool = False
    ) -> OrganizationResult:
        """Re-sort files already inside the Autosort/ output folder.

        Recursively walks ``source_path/Autosort/``, re-categorises every file
        against the current rules, and moves only those whose correct
        destination differs from their current location.
        """
        autosort_root = self.path_manager.get_target_path(source_path)
        if not autosort_root.is_dir():
            return OrganizationResult(
                success=False,
                files_processed=0,
                files_moved=0,
                errors=1,
                operations=[],
                error_log=[f"No Autosort folder found at {autosort_root}"],
            )
        files = self._scan_files_recursive(autosort_root)
        if not files:
            return OrganizationResult(
                success=True,
                files_processed=0,
                files_moved=0,
                errors=0,
                operations=[],
                error_log=[],
            )
        return self._process_resort(files, autosort_root, dry_run)

    def analyze_files(self, source_path: Path) -> Dict[str, Any]:
        try:
            files = self._scan_files(source_path)
            category_stats: Dict[str, Any] = {}
            total_size = 0
            for fp in files:
                category_folder, rule_folder, rule_name = self._categorize_file(fp)
                size = fp.stat().st_size
                if category_folder not in category_stats:
                    category_stats[category_folder] = {
                        "count": 0,
                        "size": 0,
                        "rules": {},
                    }
                category_stats[category_folder]["count"] += 1
                category_stats[category_folder]["size"] += size
                total_size += size
                sub_key = rule_folder or rule_name or ""
                if sub_key:
                    subs = category_stats[category_folder]["rules"]
                    if sub_key not in subs:
                        subs[sub_key] = {"count": 0, "size": 0, "rule_name": rule_name}
                    subs[sub_key]["count"] += 1
                    subs[sub_key]["size"] += size
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

    def _scan_files_recursive(self, root: Path) -> List[Path]:
        result = []
        try:
            for item in root.rglob("*"):
                if not item.is_file():
                    continue
                if self._should_skip_file(item):
                    continue
                if self._should_ignore_file(item):
                    continue
                result.append(item)
        except Exception as e:
            logger.error(f"Error scanning directory tree: {e}")
        return result

    _ALWAYS_SKIP = frozenset({
        ".DS_Store", "Thumbs.db", "desktop.ini", ".sortignore",
    })

    def _should_skip_file(self, file_path: Path) -> bool:
        return file_path.name in self._ALWAYS_SKIP

    def _should_ignore_file(self, file_path: Path) -> bool:
        return any(fnmatch.fnmatch(file_path.name, p) for p in self.ignore_patterns)

    def _resolve_category_config(self, category_folder_name: str) -> Optional[Category]:
        for _key, cat in self.categories.items():
            if cat.folder_name == category_folder_name:
                return cat
        return None

    def _categorize_file(self, file_path: Path) -> Tuple[str, str, str]:
        ext = file_path.suffix.lower()
        category_folder = self.extension_map.get(ext, "Miscellaneous")
        cat = self._resolve_category_config(category_folder)
        if not cat:
            return category_folder, "", ""
        rule_folder, rule_name = _evaluate_rules_for_category(file_path, cat)
        return category_folder, rule_folder, rule_name

    def _destination_dir(self, target_path: Path, category_folder: str, rule_folder: str) -> Path:
        dest = target_path / category_folder
        if rule_folder:
            dest = dest.joinpath(*Path(rule_folder).parts)
        return dest

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
                category_folder, rule_folder, rule_name = self._categorize_file(fp)
                dest_dir = self._destination_dir(target_path, category_folder, rule_folder)
                if not dry_run and not self.path_manager.ensure_directory(dest_dir):
                    error_log.append(f"Failed to create directory: {dest_dir}")
                    errors += 1
                    continue
                dest_file = self._get_unique_path(dest_dir / fp.name)
                op = FileOperation(
                    operation_type=OperationType.MOVE,
                    source=fp,
                    destination=dest_file,
                    metadata={
                        "category_folder": category_folder,
                        "rule_folder": rule_folder,
                        "rule_name": rule_name,
                    },
                )
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

    def _process_resort(
        self, files: List[Path], autosort_root: Path, dry_run: bool
    ) -> OrganizationResult:
        operations: List[FileOperation] = []
        error_log: List[str] = []
        files_moved = 0
        errors = 0

        for i, fp in enumerate(files):
            try:
                if self.progress_callback:
                    self.progress_callback(i + 1, len(files), fp.name)
                category_folder, rule_folder, rule_name = self._categorize_file(fp)
                dest_dir = self._destination_dir(autosort_root, category_folder, rule_folder)
                dest_file = dest_dir / fp.name
                if fp.parent.resolve() == dest_dir.resolve():
                    continue
                if dest_file.exists() and dest_file.resolve() == fp.resolve():
                    continue
                dest_file = self._get_unique_path(dest_file)
                op = FileOperation(
                    operation_type=OperationType.MOVE,
                    source=fp,
                    destination=dest_file,
                    metadata={
                        "category_folder": category_folder,
                        "rule_folder": rule_folder,
                        "rule_name": rule_name,
                    },
                )
                if dry_run:
                    operations.append(op)
                else:
                    if not self.path_manager.ensure_directory(dest_dir):
                        error_log.append(f"Failed to create directory: {dest_dir}")
                        errors += 1
                        continue
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

        if not dry_run:
            self._prune_empty_dirs(autosort_root)

        return OrganizationResult(
            success=errors == 0,
            files_processed=len(files),
            files_moved=files_moved,
            errors=errors,
            operations=operations,
            error_log=error_log,
        )

    @staticmethod
    def _prune_empty_dirs(root: Path) -> None:
        """Remove empty subdirectories left behind after re-sorting (bottom-up)."""
        for dirpath in sorted(root.rglob("*"), key=lambda p: -len(p.parts)):
            if dirpath.is_dir():
                try:
                    remaining = [
                        c for c in dirpath.iterdir()
                        if c.name not in (".DS_Store", "Thumbs.db", "desktop.ini")
                    ]
                    if not remaining:
                        for junk in dirpath.iterdir():
                            junk.unlink(missing_ok=True)
                        dirpath.rmdir()
                except OSError:
                    pass

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
