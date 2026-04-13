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
        return {"metadata": {"version": "3.0", "auto_generated": True}, "categories": {}}


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
class Subcategory:
    folder_name: str
    patterns: List[str] = field(default_factory=list)
    exif_indicators: List[str] = field(default_factory=list)
    extensions: List[str] = field(default_factory=list)


@dataclass
class Category:
    extensions: List[str]
    folder_name: str
    subcategories: Dict[str, Subcategory] = field(default_factory=dict)


class ConfigMigrator:
    """Applies versioned config migrations."""

    _CHAIN = {"2.1": "2.2", "2.2": "2.3", "2.3": "3.0"}

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
            subs = {}
            for sn, sd in data.get("subcategories", {}).items():
                subs[sn] = Subcategory(
                    folder_name=sd.get("folder_name", sn),
                    patterns=sd.get("patterns", []),
                    exif_indicators=sd.get("exif_indicators", []),
                    extensions=sd.get("extensions", []),
                )
            cats[name] = Category(
                extensions=data.get("extensions", []),
                folder_name=data.get("folder_name", name),
                subcategories=subs,
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
        self.config.setdefault("categories", {})[name] = {"extensions": extensions, "folder_name": folder_name}
        self._mark_user_modified()
        return self.save_config()

    def update_category(self, name: str, **kwargs) -> bool:
        cat = self.config.get("categories", {}).get(name)
        if cat is None:
            return False
        for k, v in kwargs.items():
            if k in ("extensions", "folder_name", "subcategories"):
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
        updated.setdefault("metadata", {})["version"] = self._defaults.get("metadata", {}).get("version", "3.0")
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
