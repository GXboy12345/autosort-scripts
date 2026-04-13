"""Configuration management for AutoSort."""

from __future__ import annotations

import copy
import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from itertools import zip_longest
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() / ".config" / "autosort"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.json"


def _load_bundled_defaults() -> Dict[str, Any]:
    """Load the default config shipped with the package."""
    try:
        import importlib.resources as resources
        ref = resources.files("autosort.data").joinpath("default_config.json")
        return json.loads(ref.read_text(encoding="utf-8"))
    except Exception:
        return {"metadata": {"version": "3.1", "auto_generated": True}, "categories": {}}


def _compare_versions(a: str, b: str) -> int:
    """Return 1 if a>b, -1 if a<b, 0 if equal."""
    va = [int(p) for p in a.split(".") if p.isdigit()]
    vb = [int(p) for p in b.split(".") if p.isdigit()]
    for x, y in zip_longest(va, vb, fillvalue=0):
        if x > y:
            return 1
        if x < y:
            return -1
    return 0


class ConfigStatus(Enum):
    LOADED = "loaded"
    CREATED = "created"
    ERROR = "error"
    UPDATED = "updated"


@dataclass
class MatchCondition:
    """One rule condition; values are OR-matched when multiple entries exist."""

    type: str
    values: List[Any] = field(default_factory=list)
    value: Optional[Any] = None

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> MatchCondition:
        return cls(
            type=str(raw.get("type", "")).lower(),
            values=list(raw.get("values", [])) if raw.get("values") is not None else [],
            value=raw.get("value"),
        )

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"type": self.type}
        if self.values:
            d["values"] = self.values
        if self.value is not None:
            d["value"] = self.value
        return d


@dataclass
class SortRule:
    """Ordered sort rule: first matching rule (by priority) wins.

    match_mode ``all`` requires every condition to pass (AND).
    match_mode ``any`` requires at least one condition to pass (OR) — used when
    migrating legacy subcategories where extension, glob, and exif were ORed.
    """

    name: str
    folder: str
    priority: int
    conditions: List[MatchCondition] = field(default_factory=list)
    match_mode: str = "all"  # "all" | "any"

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> SortRule:
        conds = [MatchCondition.from_dict(c) for c in raw.get("conditions", []) if isinstance(c, dict)]
        return cls(
            name=str(raw.get("name", "")),
            folder=str(raw.get("folder", "")),
            priority=int(raw.get("priority", 0)),
            conditions=conds,
            match_mode=str(raw.get("match_mode", "all")).lower(),
        )

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "name": self.name,
            "folder": self.folder,
            "priority": self.priority,
            "conditions": [c.to_dict() for c in self.conditions],
        }
        if self.match_mode != "all":
            d["match_mode"] = self.match_mode
        return d


@dataclass
class Category:
    extensions: List[str]
    folder_name: str
    rules: List[SortRule] = field(default_factory=list)


def _legacy_exif_to_condition_dicts(exif_indicators: List[str]) -> List[Dict[str, Any]]:
    """Map legacy exif_indicators to v3.1 condition dicts."""
    out: List[Dict[str, Any]] = []
    literals: List[str] = []
    has_cam = False
    for ind in exif_indicators:
        il = str(ind).lower()
        if il in ("camera_make", "camera_model", "camera_info"):
            has_cam = True
        elif il in ("screenshot_software", "screenshot"):
            out.append({"type": "exif_screenshot_like"})
        elif il in ("web_browser", "download_software"):
            continue
        else:
            literals.append(str(ind))
    if has_cam:
        out.append({"type": "exif_camera"})
    if literals:
        out.append({"type": "exif_contains", "values": literals})
    return out


def rules_from_legacy_subcategories(subcategories: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert legacy ``subcategories`` dict to ``rules`` JSON objects (unordered)."""
    raw_rules: List[Dict[str, Any]] = []
    priority = 1000
    for key, sd in subcategories.items():
        if not isinstance(sd, dict):
            continue
        folder = str(sd.get("folder_name", key))
        conditions: List[Dict[str, Any]] = []
        exts = sd.get("extensions") or []
        if exts:
            conditions.append({"type": "extension", "values": list(exts)})
        pats = sd.get("patterns") or []
        if pats:
            conditions.append({"type": "glob", "values": list(pats)})
        for c in _legacy_exif_to_condition_dicts(list(sd.get("exif_indicators") or [])):
            conditions.append(c)
        if not conditions:
            continue
        match_mode = "any" if len(conditions) > 1 else "all"
        raw_rules.append(
            {
                "name": str(key),
                "folder": folder,
                "priority": priority,
                "conditions": conditions,
                "match_mode": match_mode,
            }
        )
        priority -= 1
    raw_rules.sort(key=lambda r: -int(r.get("priority", 0)))
    return raw_rules


def parse_sort_rules_from_category_data(data: Dict[str, Any]) -> List[SortRule]:
    """Build ``SortRule`` list from category JSON (``rules`` or legacy ``subcategories``)."""
    rules_raw = data.get("rules")
    if isinstance(rules_raw, list) and rules_raw:
        rules = [SortRule.from_dict(r) for r in rules_raw if isinstance(r, dict)]
        rules.sort(key=lambda r: (-r.priority, r.name))
        return rules
    subs = data.get("subcategories")
    if isinstance(subs, dict) and subs:
        legacy = rules_from_legacy_subcategories(subs)
        rules = [SortRule.from_dict(r) for r in legacy]
        rules.sort(key=lambda r: (-r.priority, r.name))
        return rules
    return []


def merge_subcategory_extensions_into_category(cat: Dict[str, Any]) -> None:
    """Union all subcategory extensions into the category ``extensions`` list."""
    exts: List[str] = []
    seen = set()

    def add_ext(e: Any) -> None:
        if e is None:
            return
        if e == "":
            if "" not in seen:
                seen.add("")
                exts.append("")
            return
        raw = str(e).strip()
        if not raw:
            return
        norm = raw.lower() if raw.startswith(".") else f".{raw.lower().lstrip('.')}"
        if norm not in seen:
            seen.add(norm)
            exts.append(norm)

    for e in cat.get("extensions", []):
        add_ext(e)
    subs = cat.get("subcategories") or {}
    if not isinstance(subs, dict):
        return
    for sd in subs.values():
        if not isinstance(sd, dict):
            continue
        for e in sd.get("extensions") or []:
            add_ext(e)
    nonempty = sorted([x for x in exts if x != ""], key=str.lower)
    empty = [""] if "" in exts else []
    cat["extensions"] = nonempty + empty


class ConfigMigrator:
    """Applies versioned config migrations."""

    _CHAIN = {"2.1": "2.2", "2.2": "2.3", "2.3": "3.0", "3.0": "3.1"}

    def migrate(self, config: Dict, from_ver: str, to_ver: str) -> Dict:
        current = from_ver
        cfg = copy.deepcopy(config)
        while _compare_versions(to_ver, current) > 0:
            nxt = self._CHAIN.get(current)
            if nxt is None:
                break
            cfg = self._apply(cfg, current, nxt)
            current = nxt
        return cfg

    def _apply(self, cfg: Dict, _from: str, to: str) -> Dict:
        cfg.setdefault("metadata", {})["version"] = to
        cfg["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        if to == "2.2":
            cats = cfg.setdefault("categories", {})
            if "TheaterTechnology" not in cats:
                cats["TheaterTechnology"] = {"extensions": [".tmix", ".qlab4"], "folder_name": "Theater Technology"}
        if to == "3.1":
            cats = cfg.setdefault("categories", {})
            for _name, cat in cats.items():
                if not isinstance(cat, dict):
                    continue
                subs = cat.get("subcategories")
                if isinstance(subs, dict) and subs:
                    merge_subcategory_extensions_into_category(cat)
                    cat["rules"] = rules_from_legacy_subcategories(subs)
                    del cat["subcategories"]
        return cfg


class ConfigManager:
    """Loads, saves, validates, and migrates AutoSort configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config: Dict[str, Any] = {}
        self.status = ConfigStatus.ERROR
        self.error_message = ""
        self._defaults = _load_bundled_defaults()
        self._migrator = ConfigMigrator()

    def load_config(self) -> bool:
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                if not self._validate():
                    self.status = ConfigStatus.ERROR
                    self.error_message = "Validation failed"
                    return False
                migrated = self._try_migrate(self.config)
                if migrated is not self.config:
                    self.config = migrated
                    self.save_config()
                auto = self.config.get("metadata", {}).get("auto_generated", False)
                if auto:
                    dv = self._defaults.get("metadata", {}).get("version", "0")
                    cv = str(self.config.get("metadata", {}).get("version", "0"))
                    if _compare_versions(dv, cv) > 0:
                        self.config = self.update_with_defaults(self.config)
                        self.save_config()
                self.status = ConfigStatus.LOADED
                return True
            else:
                self.config = copy.deepcopy(self._defaults)
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                if self.save_config():
                    self.status = ConfigStatus.CREATED
                    return True
                self.status = ConfigStatus.ERROR
                self.error_message = "Failed to write default config"
                return False
        except json.JSONDecodeError as e:
            self.status = ConfigStatus.ERROR
            self.error_message = f"Invalid JSON: {e}"
            return False
        except Exception as e:
            self.status = ConfigStatus.ERROR
            self.error_message = str(e)
            return False

    def save_config(self) -> bool:
        try:
            self.config.setdefault("metadata", {})["last_modified"] = datetime.now().isoformat()
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False

    def get_categories(self) -> Dict[str, Category]:
        cats: Dict[str, Category] = {}
        for name, data in self.config.get("categories", {}).items():
            if not isinstance(data, dict):
                continue
            rules = parse_sort_rules_from_category_data(data)
            cats[name] = Category(
                extensions=data.get("extensions", []),
                folder_name=data.get("folder_name", name),
                rules=rules,
            )
        return cats

    def get_extension_mapping(self) -> Dict[str, str]:
        ext_map: Dict[str, str] = {}
        for _name, data in self.config.get("categories", {}).items():
            folder = data.get("folder_name", _name)
            for ext in data.get("extensions", []):
                ext_map[ext.lower()] = folder
        return ext_map

    def add_category(self, name: str, extensions: List[str], folder_name: str) -> bool:
        self.config.setdefault("categories", {})[name] = {
            "extensions": extensions,
            "folder_name": folder_name,
            "rules": [],
        }
        self._mark_user_modified()
        return self.save_config()

    def update_category(self, name: str, **kwargs) -> bool:
        cat = self.config.get("categories", {}).get(name)
        if cat is None:
            return False
        for k, v in kwargs.items():
            if k in ("extensions", "folder_name", "subcategories", "rules"):
                cat[k] = v
        self._mark_user_modified()
        return self.save_config()

    def remove_category(self, name: str) -> bool:
        if name not in self.config.get("categories", {}):
            return False
        del self.config["categories"][name]
        self._mark_user_modified()
        return self.save_config()

    def reset_to_defaults(self) -> bool:
        self.config = copy.deepcopy(self._defaults)
        return self.save_config()

    def get_config(self) -> Dict[str, Any]:
        return copy.deepcopy(self.config)

    def set_config(self, config: Dict[str, Any]) -> bool:
        self.config = copy.deepcopy(config)
        return self.save_config()

    def get_default_config(self) -> Dict[str, Any]:
        return copy.deepcopy(self._defaults)

    def get_status_info(self) -> Dict[str, Any]:
        md = self.config.get("metadata", {})
        return {
            "status": self.status.value,
            "error_message": self.error_message,
            "version": md.get("version", "unknown"),
            "auto_generated": md.get("auto_generated", True),
            "last_updated": md.get("last_updated", ""),
            "last_modified": md.get("last_modified", ""),
            "categories_count": len(self.config.get("categories", {})),
        }

    def update_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        updated = copy.deepcopy(config)
        for cat_name, default_cat in self._defaults.get("categories", {}).items():
            if cat_name not in updated.get("categories", {}):
                updated.setdefault("categories", {})[cat_name] = copy.deepcopy(default_cat)
            else:
                cur_exts = set(updated["categories"][cat_name].get("extensions", []))
                def_exts = set(default_cat.get("extensions", []))
                updated["categories"][cat_name]["extensions"] = sorted(cur_exts | def_exts)
                updated["categories"][cat_name].setdefault("folder_name", default_cat.get("folder_name", cat_name))
                def_rules = default_cat.get("rules")
                if isinstance(def_rules, list) and def_rules:
                    if not updated["categories"][cat_name].get("rules"):
                        updated["categories"][cat_name]["rules"] = copy.deepcopy(def_rules)
        updated.setdefault("metadata", {})["version"] = self._defaults.get("metadata", {}).get("version", "3.1")
        return updated

    def _validate(self) -> bool:
        if "metadata" not in self.config or "version" not in self.config["metadata"]:
            return False
        cats = self.config.get("categories")
        if not isinstance(cats, dict):
            return False
        for name, data in cats.items():
            if not isinstance(data, dict) or not isinstance(data.get("extensions"), list):
                return False
        return True

    def _mark_user_modified(self):
        md = self.config.setdefault("metadata", {})
        md["auto_generated"] = False
        md["last_modified"] = datetime.now().isoformat()

    def _try_migrate(self, config: Dict) -> Dict:
        cur = config.get("metadata", {}).get("version", "1.0")
        target = self._defaults.get("metadata", {}).get("version", "3.0")
        if _compare_versions(target, cur) > 0:
            backup = self._backup()
            try:
                return self._migrator.migrate(config, cur, target)
            except Exception as e:
                logger.error(f"Migration failed: {e}")
                if backup:
                    self._restore(backup)
                return config
        return config

    def _backup(self) -> str:
        if not self.config_path.exists():
            return ""
        bp = self.config_path.parent / f"config_backup_{datetime.now():%Y%m%d_%H%M%S}.json"
        try:
            shutil.copy2(self.config_path, bp)
            return str(bp)
        except Exception:
            return ""

    def _restore(self, backup_path: str) -> bool:
        try:
            shutil.copy2(backup_path, self.config_path)
            return True
        except Exception:
            return False
