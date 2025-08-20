"""
Configuration Manager for AutoSort

Handles loading, saving, and managing configuration files with validation,
version checking, and user-friendly error handling.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import urllib.request
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ConfigStatus(Enum):
    """Configuration status enumeration."""
    LOADED = "loaded"
    CREATED = "created"
    ERROR = "error"
    UPDATED = "updated"


@dataclass
class ConfigMetadata:
    """Configuration metadata structure."""
    version: str
    auto_generated: bool = True
    last_updated: str = ""
    last_modified: str = ""
    note: str = ""


@dataclass
class Subcategory:
    """Subcategory configuration structure."""
    folder_name: str
    patterns: List[str] = None
    exif_indicators: List[str] = None
    extensions: List[str] = None
    
    def __post_init__(self):
        if self.patterns is None:
            self.patterns = []
        if self.exif_indicators is None:
            self.exif_indicators = []
        if self.extensions is None:
            self.extensions = []


@dataclass
class Category:
    """Category configuration structure."""
    extensions: List[str]
    folder_name: str
    subcategories: Dict[str, Subcategory] = None
    
    def __post_init__(self):
        if self.subcategories is None:
            self.subcategories = {}


class ConfigManager:
    """
    Manages AutoSort configuration with validation and error handling.
    
    This class handles loading, saving, and updating configuration files
    with proper validation, version checking, and user-friendly error messages.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file (default: autosort_config.json)
        """
        self.config_path = config_path or Path("autosort_config.json")
        self.config: Dict[str, Any] = {}
        self.status = ConfigStatus.ERROR
        self.error_message = ""
        
        # Default configuration
        self._default_config = self._create_default_config()
    
    def load_config(self) -> bool:
        """
        Load configuration from file or create default if not exists.
        
        Returns:
            True if configuration loaded successfully, False otherwise
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                
                if self._validate_config():
                    self.status = ConfigStatus.LOADED
                    logger.info(f"Configuration loaded from {self.config_path}")
                    
                    # Show configuration status
                    auto_generated = self.config.get("metadata", {}).get("auto_generated", False)
                    if auto_generated:
                        print("ℹ️  Auto-generated configuration")
                        
                        # Check if we need to update from DEFAULT_CONFIG
                        default_version = self._default_config.get("metadata", {}).get("version", "0")
                        config_version = str(self.config.get("metadata", {}).get("version", "0"))
                        
                        if self._is_version_newer(default_version, config_version):
                            print("🔄 Auto-updating configuration from built-in defaults...")
                            updated_config = self.update_with_defaults(self.config)
                            if updated_config != self.config:
                                self.config = updated_config
                                if self.save_config():
                                    print(f"✅ Auto-updated configuration from version {config_version} to {default_version}")
                                else:
                                    print("❌ Failed to save updated configuration")
                            else:
                                print("✅ Configuration already up to date with built-in defaults")
                    else:
                        print("ℹ️  User-modified configuration (auto-updates disabled)")
                    
                    # Check for remote updates
                    self._check_for_updates()
                    
                    # Pause to let user read the configuration status
                    import time
                    time.sleep(1.5)
                    return True
                else:
                    self.status = ConfigStatus.ERROR
                    self.error_message = "Configuration validation failed"
                    logger.error("Configuration validation failed")
                    return False
            else:
                # Create default configuration
                self.config = self._default_config.copy()
                if self.save_config():
                    self.status = ConfigStatus.CREATED
                    logger.info(f"Default configuration created at {self.config_path}")
                    
                    # Check for remote updates
                    self._check_for_updates()
                    
                    # Pause to let user read the configuration status
                    import time
                    time.sleep(1.5)
                    return True
                else:
                    self.status = ConfigStatus.ERROR
                    self.error_message = "Failed to create default configuration"
                    logger.error("Failed to create default configuration")
                    return False
                    
        except json.JSONDecodeError as e:
            self.status = ConfigStatus.ERROR
            self.error_message = f"Invalid JSON in configuration file: {e}"
            logger.error(f"Invalid JSON in configuration file: {e}")
            return False
        except Exception as e:
            self.status = ConfigStatus.ERROR
            self.error_message = f"Error loading configuration: {e}"
            logger.error(f"Error loading configuration: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Update metadata
            if "metadata" not in self.config:
                self.config["metadata"] = {}
            
            self.config["metadata"]["last_modified"] = datetime.now().isoformat()
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_categories(self) -> Dict[str, Category]:
        """
        Get categories from configuration.
        
        Returns:
            Dictionary of category objects
        """
        categories = {}
        for name, data in self.config.get("categories", {}).items():
            subcategories = {}
            for sub_name, sub_data in data.get("subcategories", {}).items():
                subcategories[sub_name] = Subcategory(
                    folder_name=sub_data.get("folder_name", sub_name),
                    patterns=sub_data.get("patterns", []),
                    exif_indicators=sub_data.get("exif_indicators", []),
                    extensions=sub_data.get("extensions", [])
                )
            
            categories[name] = Category(
                extensions=data.get("extensions", []),
                folder_name=data.get("folder_name", name),
                subcategories=subcategories
            )
        
        return categories
    
    def add_category(self, name: str, extensions: List[str], folder_name: str) -> bool:
        """
        Add a new category to the configuration.
        
        Args:
            name: Category name
            extensions: List of file extensions
            folder_name: Folder name for the category
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            if "categories" not in self.config:
                self.config["categories"] = {}
            
            self.config["categories"][name] = {
                "extensions": extensions,
                "folder_name": folder_name
            }
            
            # Mark as user-modified
            self._mark_user_modified()
            
            return self.save_config()
            
        except Exception as e:
            logger.error(f"Error adding category: {e}")
            return False
    
    def update_category(self, name: str, **kwargs) -> bool:
        """
        Update an existing category.
        
        Args:
            name: Category name
            **kwargs: Category properties to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            if name not in self.config.get("categories", {}):
                logger.error(f"Category '{name}' not found")
                return False
            
            category = self.config["categories"][name]
            
            for key, value in kwargs.items():
                if key in ["extensions", "folder_name", "subcategories"]:
                    category[key] = value
            
            # Mark as user-modified
            self._mark_user_modified()
            
            return self.save_config()
            
        except Exception as e:
            logger.error(f"Error updating category: {e}")
            return False
    
    def remove_category(self, name: str) -> bool:
        """
        Remove a category from the configuration.
        
        Args:
            name: Category name to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            if name not in self.config.get("categories", {}):
                logger.error(f"Category '{name}' not found")
                return False
            
            del self.config["categories"][name]
            
            # Mark as user-modified
            self._mark_user_modified()
            
            return self.save_config()
            
        except Exception as e:
            logger.error(f"Error removing category: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to defaults.
        
        Returns:
            True if reset successfully, False otherwise
        """
        try:
            self.config = self._default_config.copy()
            return self.save_config()
            
        except Exception as e:
            logger.error(f"Error resetting to defaults: {e}")
            return False
    
    def get_extension_mapping(self) -> Dict[str, str]:
        """
        Create a mapping from file extensions to category folder names.
        
        Returns:
            Dictionary mapping extensions to folder names
        """
        extension_map = {}
        
        for category_name, category_data in self.config.get("categories", {}).items():
            folder_name = category_data.get("folder_name", category_name)
            extensions = category_data.get("extensions", [])
            
            for ext in extensions:
                extension_map[ext.lower()] = folder_name
        
        return extension_map
    
    def get_status_info(self) -> Dict[str, Any]:
        """
        Get configuration status information.
        
        Returns:
            Dictionary with status information
        """
        metadata = self.config.get("metadata", {})
        
        return {
            "status": self.status.value,
            "error_message": self.error_message,
            "version": metadata.get("version", "unknown"),
            "auto_generated": metadata.get("auto_generated", True),
            "last_updated": metadata.get("last_updated", ""),
            "last_modified": metadata.get("last_modified", ""),
            "categories_count": len(self.config.get("categories", {}))
        }
    
    def _validate_config(self) -> bool:
        """
        Validate configuration structure.
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required top-level keys
            required_keys = ["metadata", "categories"]
            for key in required_keys:
                if key not in self.config:
                    logger.error(f"Missing required key: {key}")
                    return False
            
            # Validate metadata
            metadata = self.config["metadata"]
            if "version" not in metadata:
                logger.error("Missing version in metadata")
                return False
            
            # Validate categories
            categories = self.config["categories"]
            if not isinstance(categories, dict):
                logger.error("Categories must be a dictionary")
                return False
            
            for name, data in categories.items():
                if not isinstance(data, dict):
                    logger.error(f"Category '{name}' must be a dictionary")
                    return False
                
                if "extensions" not in data:
                    logger.error(f"Category '{name}' missing extensions")
                    return False
                
                if not isinstance(data["extensions"], list):
                    logger.error(f"Category '{name}' extensions must be a list")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False
    
    def _check_for_updates(self) -> None:
        """
        Check for configuration updates from remote source.
        """
        try:
            self._check_config_version()
        except Exception as e:
            logger.warning(f"Could not check for updates: {e}")
    
    def _is_version_newer(self, default_version: str, config_version: str) -> bool:
        """
        Return True if default_version is newer than config_version (simple dot-separated comparison).
        
        Args:
            default_version: Version to compare against
            config_version: Current version
            
        Returns:
            True if default_version is newer
        """
        from itertools import zip_longest
        
        def parse(v: str):
            return [int(part) for part in v.split('.') if part.isdigit()]
        
        dv = parse(default_version)
        cv = parse(config_version)
        
        for d, c in zip_longest(dv, cv, fillvalue=0):
            if d > c:
                return True
            if d < c:
                return False
        return False
    
    def _fetch_remote_config(self) -> Optional[Dict[str, Any]]:
        """
        Fetch the remote configuration from GitHub.
        
        Returns:
            Remote configuration or None if failed
        """
        remote_url = "https://raw.githubusercontent.com/GXboy12345/autosort-scripts/refs/heads/main/example_custom_config.json"
        
        try:
            import urllib.request
            with urllib.request.urlopen(remote_url, timeout=10) as response:
                remote_config = json.loads(response.read().decode('utf-8'))
                return remote_config
        except Exception as e:
            logger.warning(f"Could not fetch remote configuration: {e}")
            return None
    
    def _check_config_version(self) -> None:
        """
        Check if the local configuration is up to date with the remote version.
        """
        remote_config = self._fetch_remote_config()
        if not remote_config:
            return
        
        local_version = self.config.get("metadata", {}).get("version", "0.0")
        remote_version = remote_config.get("metadata", {}).get("version", "0.0")
        
        if self._is_version_newer(remote_version, local_version):
            print(f"📢 New configuration version available!")
            print(f"   Current version: {local_version}")
            print(f"   Remote version: {remote_version}")
            print(f"   To update: Fetch latest changes (git pull), then restart AutoSort")
            print()
        elif local_version == remote_version:
            print(f"✅ Configuration is up to date (v{local_version})")
        else:
            # Local version is newer than remote (unusual but possible)
            print(f"🔍 Local configuration is newer than remote (v{local_version} vs v{remote_version})")
            print(f"   This is unusual - you may have a development or custom version")
            print()
    
    def _mark_user_modified(self) -> None:
        """
        Mark configuration as user-modified.
        """
        if "metadata" not in self.config:
            self.config["metadata"] = {}
        
        self.config["metadata"]["auto_generated"] = False
        self.config["metadata"]["last_modified"] = datetime.now().isoformat()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        Create the default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "metadata": {
                "version": "2.1",
                "auto_generated": True,
                "last_updated": "2025-08-20",
                "note": "This is the default configuration"
            },
            "categories": {
                "Images": {
                    "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".heic", ".raw", ".svg", ".webp", ".psd", ".ai", ".eps", ".ico", ".avif", ".jxl", ".jp2", ".j2k", ".jpf", ".jpx", ".tga", ".dng", ".cr2", ".nef", ".orf", ".arw", ".icns"],
                    "folder_name": "Images",
                    "subcategories": {
                        "Screenshots": {
                            "patterns": ["Screenshot*", "Screen Shot*"],
                            "exif_indicators": ["screenshot_software"],
                            "folder_name": "Screenshots"
                        },
                        "Adobe_Edited": {
                            "exif_indicators": ["Adobe Photoshop", "Adobe Lightroom", "Adobe Camera Raw", "Adobe"],
                            "folder_name": "Adobe Edited"
                        },
                        "Camera_Photos": {
                            "exif_indicators": ["camera_make", "camera_model"],
                            "folder_name": "Camera Photos"
                        },
                        "Web_Downloads": {
                            "patterns": ["image*", "img*", "photo*"],
                            "exif_indicators": ["web_browser", "download_software"],
                            "folder_name": "Web Downloads"
                        },
                        "Design_Files": {
                            "extensions": [".psd", ".ai", ".eps", ".sketch", ".fig"],
                            "folder_name": "Design Files"
                        },
                        "RAW_Photos": {
                            "extensions": [".raw", ".dng", ".cr2", ".nef", ".arw", ".orf"],
                            "folder_name": "RAW Photos"
                        }
                    }
                },
                "Audio": {
                    "extensions": [".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".wma", ".aiff", ".alac", ".opus", ".amr", ".mid", ".midi", ".wv", ".ra", ".ape", ".dts"],
                    "folder_name": "Audio",
                    "subcategories": {
                        "Music": {
                            "patterns": ["*music*", "*song*", "*track*", "*album*", "*playlist*"],
                            "folder_name": "Music"
                        },
                        "Podcasts": {
                            "patterns": ["*podcast*", "*episode*", "*show*"],
                            "folder_name": "Podcasts"
                        },
                        "Voice_Recordings": {
                            "patterns": ["*voice*", "*recording*", "*memo*", "*note*", "*interview*"],
                            "folder_name": "Voice Recordings"
                        },
                        "Sound_Effects": {
                            "patterns": ["*sfx*", "*sound*", "*effect*", "*audio*"],
                            "folder_name": "Sound Effects"
                        },
                        "Audiobooks": {
                            "patterns": ["*audiobook*", "*book*", "*chapter*"],
                            "folder_name": "Audiobooks"
                        }
                    }
                },
                "Video": {
                    "extensions": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm", ".m4v", ".3gp", ".mpeg", ".mpg", ".ts", ".m2ts", ".mts", ".m2v", ".divx", ".ogv", ".h264", ".h265", ".hevc", ".vob", ".rm", ".asf", ".mxf"],
                    "folder_name": "Video",
                    "subcategories": {
                        "Movies": {
                            "patterns": ["*movie*", "*film*", "*cinema*"],
                            "folder_name": "Movies"
                        },
                        "TV_Shows": {
                            "patterns": ["*episode*", "*season*", "*series*", "*show*"],
                            "folder_name": "TV Shows"
                        },
                        "Tutorials": {
                            "patterns": ["*tutorial*", "*howto*", "*guide*", "*lesson*", "*course*"],
                            "folder_name": "Tutorials"
                        },
                        "Screen_Recordings": {
                            "patterns": ["*screen*", "*recording*", "*capture*", "*demo*"],
                            "folder_name": "Screen Recordings"
                        },
                        "Home_Videos": {
                            "patterns": ["*home*", "*family*", "*personal*", "*vacation*", "*trip*"],
                            "folder_name": "Home Videos"
                        }
                    }
                },
                "Text": {
                    "extensions": [".txt", ".md", ".rtf", ".log", ".csv", ".tex", ".json", ".xml", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".toml", ".adoc", ".asciidoc", ".rst", ".properties"],
                    "folder_name": "Text",
                    "subcategories": {
                        "Markdown": {
                            "extensions": [".md", ".markdown"],
                            "folder_name": "Markdown"
                        },
                        "Logs": {
                            "extensions": [".log"],
                            "patterns": ["*log*", "*error*", "*debug*"],
                            "folder_name": "Logs"
                        },
                        "Data": {
                            "extensions": [".csv", ".json", ".xml", ".yaml", ".yml"],
                            "folder_name": "Data"
                        },
                        "Config": {
                            "extensions": [".ini", ".cfg", ".conf", ".toml", ".properties"],
                            "folder_name": "Config"
                        },
                        "Notes": {
                            "patterns": ["*note*", "*todo*", "*readme*"],
                            "folder_name": "Notes"
                        }
                    }
                },
                "Documents": {
                    "extensions": [".pdf", ".doc", ".docx", ".pages", ".odt"],
                    "folder_name": "Documents",
                    "subcategories": {
                        "PDFs": {
                            "extensions": [".pdf"],
                            "folder_name": "PDFs"
                        },
                        "Word_Documents": {
                            "extensions": [".doc", ".docx", ".odt"],
                            "folder_name": "Word Documents"
                        },
                        "Pages_Documents": {
                            "extensions": [".pages"],
                            "folder_name": "Pages Documents"
                        },
                        "Scanned_Documents": {
                            "patterns": ["*scan*", "*scanned*", "*document*"],
                            "folder_name": "Scanned Documents"
                        }
                    }
                },
                "Code": {
                    "extensions": [".py", ".js", ".sh", ".rb", ".pl", ".c", ".cpp", ".h", ".java", ".go", ".rs", ".ts", ".jsx", ".tsx", ".php", ".swift", ".kt", ".kts", ".scala", ".ps1", ".cs", ".dart", ".r", ".m", ".lua", ".html", ".htm", ".css", ".scss", ".less", ".vue", ".svelte", ".sql"],
                    "folder_name": "Code",
                    "subcategories": {
                        "Python": {
                            "extensions": [".py", ".pyc", ".pyo", ".pyd"],
                            "folder_name": "Python"
                        },
                        "JavaScript": {
                            "extensions": [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"],
                            "folder_name": "JavaScript"
                        },
                        "Web": {
                            "extensions": [".html", ".htm", ".css", ".scss", ".less", ".sass", ".vue", ".svelte"],
                            "folder_name": "Web"
                        },
                        "Scripts": {
                            "extensions": [".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd"],
                            "folder_name": "Scripts"
                        },
                        "Mobile": {
                            "extensions": [".swift", ".kt", ".kts", ".dart"],
                            "folder_name": "Mobile"
                        },
                        "Data_Science": {
                            "extensions": [".r", ".m", ".ipynb", ".rdata"],
                            "folder_name": "Data Science"
                        }
                    }
                },
                "Archives": {
                    "extensions": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz", ".tar.gz", ".tar.bz2", ".tar.xz", ".zst", ".zstd", ".lz", ".lzma", ".cab", ".ace", ".arj"],
                    "folder_name": "Archives",
                    "subcategories": {
                        "Compressed": {
                            "extensions": [".zip", ".rar", ".7z", ".cab", ".ace", ".arj"],
                            "folder_name": "Compressed"
                        },
                        "Tarballs": {
                            "extensions": [".tar", ".tar.gz", ".tar.bz2", ".tar.xz", ".tgz"],
                            "folder_name": "Tarballs"
                        },
                        "Backups": {
                            "patterns": ["*backup*", "*backup*", "*backup*"],
                            "folder_name": "Backups"
                        },
                        "Downloads": {
                            "patterns": ["*download*", "*downloaded*"],
                            "folder_name": "Downloads"
                        }
                    }
                },
                "Minecraft": {
                    "extensions": [".jar", ".schem", ".schematic", ".litematic", ".nbt", ".mcfunction"],
                    "folder_name": "Minecraft"
                },
                "NonMac": {
                    "extensions": [".exe", ".msi", ".dll", ".com", ".bat", ".cmd", ".sys", ".appimage", ".scr", ".rpm", ".cab", ".pkg"],
                    "folder_name": "Non-Mac Files"
                },
                "DiskImages": {
                    "extensions": [".dmg", ".iso", ".img", ".bin", ".toast", ".toast.gz", ".toast.bz2", ".toast.xz", ".toast.tar", ".toast.tar.gz", ".toast.tar.bz2", ".toast.tar.xz", ".vhd", ".vhdx", ".vmdk", ".qcow2"],
                    "folder_name": "Disk Images"
                },
                "MusicScores": {
                    "extensions": [".mscz", ".mscx", ".mscx.gz", ".mscx.bz2", ".mscx.xz", ".mscx.tar", ".mscx.tar.gz", ".mscx.tar.bz2", ".mscx.tar.xz"],
                    "folder_name": "Music Scores"
                },
                "3DModels": {
                    "extensions": [".stl", ".obj", ".fbx", ".dae", ".3ds", ".ply", ".glb", ".gltf", ".blend", ".3mf", ".igs", ".iges", ".stp", ".step"],
                    "folder_name": "3D Models",
                    "subcategories": {
                        "Print_Ready": {
                            "extensions": [".stl", ".3mf"],
                            "folder_name": "Print Ready"
                        },
                        "CAD_Models": {
                            "extensions": [".igs", ".iges", ".stp", ".step"],
                            "folder_name": "CAD Models"
                        },
                        "Game_Assets": {
                            "extensions": [".fbx", ".glb", ".gltf"],
                            "folder_name": "Game Assets"
                        },
                        "Blender_Files": {
                            "extensions": [".blend"],
                            "folder_name": "Blender Files"
                        },
                        "Scanned_Models": {
                            "patterns": ["*scan*", "*scanned*"],
                            "folder_name": "Scanned Models"
                        }
                    }
                },
                "eBooks": {
                    "extensions": [".epub", ".mobi", ".azw", ".azw3", ".fb2"],
                    "folder_name": "eBooks"
                },
                "Fonts": {
                    "extensions": [".ttf", ".otf", ".woff", ".woff2", ".fnt"],
                    "folder_name": "Fonts"
                },
                "Contact files": {
                    "extensions": [".vcf", ".vcard"],
                    "folder_name": "Contact files"
                },
                "Databases": {
                    "extensions": [".db", ".sqlite", ".sql", ".mdb", ".accdb", ".odb", ".dbf"],
                    "folder_name": "Databases"
                },
                "Certificates": {
                    "extensions": [".pem", ".cer", ".crt", ".pfx", ".p12", ".der", ".csr", ".key", ".p7b", ".p7c"],
                    "folder_name": "Certificates"
                },
                "GIS": {
                    "extensions": [".shp", ".kml", ".kmz", ".gpx", ".geojson", ".gml", ".tif", ".tiff", ".img", ".asc"],
                    "folder_name": "GIS"
                },
                "VideoProjects": {
                    "extensions": [".prproj", ".veg", ".drp", ".fcpxml", ".aep"],
                    "folder_name": "Video Projects"
                },
                "AudioProjects": {
                    "extensions": [".flp", ".als", ".aup", ".aup3", ".sesx", ".ptx", ".rpp", ".rpl", ".rpreset", ".rpp.gz", ".rpp.bz2", ".rpp.xz", ".rpp.tar", ".rpp.tar.gz", ".rpp.tar.bz2", ".rpp.tar.xz"],
                    "folder_name": "Audio Projects"
                },
                "Spreadsheets": {
                    "extensions": [".xls", ".xlsx", ".xlsm", ".csv", ".tsv"],
                    "folder_name": "Spreadsheets"
                },
                "Presentations": {
                    "extensions": [".ppt", ".pptx", ".pps", ".ppsx"],
                    "folder_name": "Presentations"
                },
                "Torrents": {
                    "extensions": [".torrent"],
                    "folder_name": "Torrents"
                },
                "Sideloading": {
                    "extensions": [".ipa", ".dylib", ".xapk", ".xapk.xz", ".xapk.bz2", ".xapk.tar", ".xapk.tar.gz", ".xapk.tar.bz2", ".xapk.tar.xz", ".mobileprovision", ".mobileconfig", ".mobileconfig.xml", ".mobileconfig.xml.gz", ".mobileconfig.xml.bz2", ".mobileconfig.xml.xz", ".mobileconfig.xml.tar", ".mobileconfig.xml.tar.gz", ".mobileconfig.xml.tar.bz2", ".mobileconfig.xml.tar.xz"],
                    "folder_name": "Sideloading"
                },
                "Subtitles": {
                    "extensions": [".srt", ".sub", ".idx", ".subrip", ".subrip.gz", ".subrip.bz2", ".subrip.xz", ".subrip.tar", ".subrip.tar.gz", ".subrip.tar.bz2", ".subrip.tar.xz", ".srt.gz", ".srt.bz2", ".srt.xz", ".srt.tar", ".srt.tar.gz", ".srt.tar.bz2", ".srt.tar.xz", ".ytp", ".aegisub", ".ssa", ".ass", ".vtt", ".ttml", ".ttml.gz", ".ttml.bz2", ".ttml.xz", ".ttml.tar", ".ttml.tar.gz", ".ttml.tar.bz2", ".ttml.tar.xz"],
                    "folder_name": "Subtitles"
                },

                "Miscellaneous": {
                    "extensions": [],
                    "folder_name": "Miscellaneous"
                }
            }
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.
        
        Returns:
            Current configuration dictionary
        """
        return self.config.copy()
    
    def set_config(self, config: Dict[str, Any]) -> bool:
        """
        Set the configuration and save to file.
        
        Args:
            config: Configuration dictionary to set
            
        Returns:
            True if saved successfully, False otherwise
        """
        self.config = config.copy()
        return self.save_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return self._default_config.copy()
    
    def update_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update configuration with defaults, preserving user customizations.
        
        Args:
            config: Current configuration
            
        Returns:
            Updated configuration
        """
        import copy
        updated_config = copy.deepcopy(config)
        default_categories = self._default_config.get("categories", {})
        current_categories = config.get("categories", {})
        
        # Add new categories
        for category_name, default_category in default_categories.items():
            if category_name not in current_categories:
                updated_config["categories"][category_name] = default_category.copy()
            else:
                # Merge extensions, keeping user customizations
                current_extensions = set(current_categories[category_name].get("extensions", []))
                default_extensions = set(default_category.get("extensions", []))
                merged_extensions = list(current_extensions | default_extensions)
                
                updated_config["categories"][category_name]["extensions"] = merged_extensions
                
                # Preserve other user customizations
                if "folder_name" not in updated_config["categories"][category_name]:
                    updated_config["categories"][category_name]["folder_name"] = default_category.get("folder_name", category_name)
        
        # Update metadata version to match defaults
        if "metadata" not in updated_config:
            updated_config["metadata"] = {}
        updated_config["metadata"]["version"] = self._default_config.get("metadata", {}).get("version", "2.0")
        updated_config["metadata"]["last_updated"] = self._default_config.get("metadata", {}).get("last_updated", "2025-08-20")
        
        return updated_config
