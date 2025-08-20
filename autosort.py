#!/usr/bin/env python3
"""
AutoSort - File organizer

This script automatically organizes files into categorized folders.

Requirements:
- Python 3.6+
- macOS (for Desktop path detection and folder dialog)

Copyright (c) 2024 Gboy
Licensed under the MIT License - see LICENSE file for details.
"""

import fnmatch
import shutil
import os
import sys
import json
import re
import urllib.request
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime

# —— Configuration —— #
SCRIPT_DIR   = Path(__file__).resolve().parent
IGNORE_FILE  = SCRIPT_DIR / '.sortignore'
CONFIG_FILE  = SCRIPT_DIR / 'autosort_config.json'

# Default configuration
DEFAULT_CONFIG = {
    "metadata": {
        "version": "1.14",
        "auto_generated": True,
        "last_updated": "2024-12-01",
        "note": "This is the default configuration - auto-updates are now manual only"
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
            "folder_name": "Audio"
        },
        "Video": {
            "extensions": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm", ".m4v", ".3gp", ".mpeg", ".mpg", ".ts", ".m2ts", ".mts", ".m2v", ".divx", ".ogv", ".h264", ".h265", ".hevc", ".vob", ".rm", ".asf", ".mxf"],
            "folder_name": "Video"
        },
        "Text": {
            "extensions": [".txt", ".md", ".rtf", ".log", ".csv", ".tex", ".json", ".xml", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".toml", ".adoc", ".asciidoc", ".rst", ".properties"],
            "folder_name": "Text"
        },
        "Documents": {
            "extensions": [".pdf", ".doc", ".docx", ".pages", ".odt"],
            "folder_name": "Documents"
        },
        "Code": {
            "extensions": [".py", ".js", ".sh", ".rb", ".pl", ".c", ".cpp", ".h", ".java", ".go", ".rs", ".ts", ".jsx", ".tsx", ".php", ".swift", ".kt", ".kts", ".scala", ".ps1", ".cs", ".dart", ".r", ".m", ".lua", ".html", ".htm", ".css", ".scss", ".less", ".vue", ".svelte", ".sql"],
            "folder_name": "Code"
        },
        "Archives": {
            "extensions": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz", ".tar.gz", ".tar.bz2", ".tar.xz", ".zst", ".zstd", ".lz", ".lzma", ".cab", ".ace", ".arj"],
            "folder_name": "Archives"
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
            "folder_name": "3D Models"
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
        },
        "Miscellaneous": {
            "extensions": [],
            "folder_name": "Miscellaneous"
        }
    }
}

# macOS-specific Desktop path detection
def get_desktop_path() -> Path:
    """Get the Desktop path, handling different locales on macOS."""
    # Try common Desktop paths
    possible_paths = [
        Path.home() / 'Desktop',
        Path.home() / 'Escritorio',  # Spanish
        Path.home() / 'Bureau',       # French
        Path.home() / 'Schreibtisch', # German
        Path.home() / 'Desktop'       # Fallback
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_dir():
            return path
    
    # If none found, return the standard Desktop path
    return Path.home() / 'Desktop'

def get_downloads_path() -> Path:
    """Get the Downloads path, handling different locales on macOS."""
    # Try common Downloads paths
    possible_paths = [
        Path.home() / 'Downloads',
        Path.home() / 'Descargas',    # Spanish
        Path.home() / 'Téléchargements', # French
        Path.home() / 'Downloads'     # Fallback
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_dir():
            return path
    
    # If none found, return the standard Downloads path
    return Path.home() / 'Downloads'

def select_folder_dialog() -> Path:
    """Open a folder selection dialog and return the selected path."""
    try:
        import subprocess
        
        # Use AppleScript to open folder selection dialog
        script = '''
        tell application "System Events"
            activate
            set folderPath to choose folder with prompt "Select folder to organize:"
            return POSIX path of folderPath
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            selected_path = Path(result.stdout.strip())
            if selected_path.exists() and selected_path.is_dir():
                return selected_path
            else:
                print(f"Error: Selected path {selected_path} is not a valid directory")
                return None
        else:
            print("Folder selection was cancelled or failed")
            return None
            
    except subprocess.TimeoutExpired:
        print("Folder selection dialog timed out")
        return None
    except Exception as e:
        print(f"Error opening folder dialog: {e}")
        return None

def get_source_directory() -> tuple[Path, Path, bool]:
    """Get the source directory and target root based on user choice."""
    desktop_path = get_desktop_path()
    downloads_path = get_downloads_path()
    
    print("AutoSort - File Organizer")
    print("=" * 40)
    print(f"1. Organize Desktop ({desktop_path})")
    print(f"2. Organize Downloads ({downloads_path})")
    print("3. Organize custom folder")
    print("4. Preview Desktop organization (dry run)")
    print("5. Preview Downloads organization (dry run)")
    print("6. Preview custom folder organization (dry run)")
    print("7. Configuration wizard")
    print("8. Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == "1":
                source_dir = desktop_path
                target_root = source_dir / 'Autosort'
                print(f"Selected: Desktop ({source_dir})")
                return source_dir, target_root, False
                
            elif choice == "2":
                source_dir = downloads_path
                target_root = source_dir / 'Autosort'
                print(f"Selected: Downloads ({source_dir})")
                return source_dir, target_root, False
                
            elif choice == "3":
                print("Opening folder selection dialog...")
                selected_path = select_folder_dialog()
                
                if selected_path:
                    source_dir = selected_path
                    target_root = source_dir / 'Autosort'
                    print(f"Selected: {source_dir}")
                    return source_dir, target_root, False
                else:
                    print("Please try again or select option 8 to exit.")
                    continue
                    
            elif choice == "4":
                print("Preview mode - no files will be moved")
                source_dir = desktop_path
                target_root = source_dir / 'Autosort'
                print(f"Previewing: Desktop ({source_dir})")
                return source_dir, target_root, True
            
            elif choice == "5":
                print("Preview mode - no files will be moved")
                source_dir = downloads_path
                target_root = source_dir / 'Autosort'
                print(f"Previewing: Downloads ({source_dir})")
                return source_dir, target_root, True
            
            elif choice == "6":
                print("Preview mode - no files will be moved")
                print("Opening folder selection dialog...")
                selected_path = select_folder_dialog()
                
                if selected_path:
                    source_dir = selected_path
                    target_root = source_dir / 'Autosort'
                    print(f"Previewing: {source_dir}")
                    return source_dir, target_root, True
                else:
                    print("Please try again or select option 8 to exit.")
                    continue
            
            elif choice == "7":
                configuration_wizard()
                # Return to main menu after wizard
                return get_source_directory()
                    
            elif choice == "8":
                print("Goodbye!")
                sys.exit(0)
                
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, 7, or 8.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.")

def is_version_newer(default_version: str, config_version: str) -> bool:
    """Return True if default_version is newer than config_version (simple dot-separated comparison)."""
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

def fetch_remote_config() -> Dict:
    """Fetch the remote configuration from GitHub."""
    remote_url = "https://raw.githubusercontent.com/GXboy12345/autosort-scripts/refs/heads/main/example_custom_config.json"
    
    try:
        with urllib.request.urlopen(remote_url, timeout=10) as response:
            remote_config = json.loads(response.read().decode('utf-8'))
            return remote_config
    except Exception as e:
        print(f"⚠️  Could not fetch remote configuration: {e}")
        return None

def check_config_version(config: Dict) -> None:
    """Check if the local configuration is up to date with the remote version."""
    remote_config = fetch_remote_config()
    if not remote_config:
        return
    
    local_version = config.get("metadata", {}).get("version", "0.0")
    remote_version = remote_config.get("metadata", {}).get("version", "0.0")
    
    if is_version_newer(remote_version, local_version):
        print(f"📢 New configuration version available!")
        print(f"   Current version: {local_version}")
        print(f"   Remote version: {remote_version}")
        print(f"   Go to Configuration wizard → Manual update from defaults to update")
        print()
    elif local_version == remote_version:
        print(f"✅ Configuration is up to date (v{local_version})")
    else:
        # Local version is newer than remote (unusual but possible)
        print(f"🔍 Local configuration is newer than remote (v{local_version} vs v{remote_version})")
        print(f"   This is unusual - you may have a development or custom version")
        print()


def load_config() -> Dict:
    """Load configuration from JSON file or create default if not exists."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"Loaded configuration from {CONFIG_FILE}")
                
                # Show configuration status
                auto_generated = config.get("metadata", {}).get("auto_generated", False)
                if auto_generated:
                    print("ℹ️  Auto-generated configuration")
                    
                    # Check if we need to update from DEFAULT_CONFIG
                    default_version = DEFAULT_CONFIG.get("metadata", {}).get("version", "0")
                    config_version = str(config.get("metadata", {}).get("version", "0"))
                    
                    if is_version_newer(default_version, config_version):
                        print("🔄 Auto-updating configuration from built-in defaults...")
                        updated_config = update_config_with_defaults(config)
                        if updated_config != config:
                            save_config(updated_config)
                            print(f"✅ Auto-updated configuration from version {config_version} to {default_version}")
                            config = updated_config
                        else:
                            print("✅ Configuration already up to date with built-in defaults")
                else:
                    print("ℹ️  User-modified configuration (auto-updates disabled)")
                
                # Check for remote updates
                check_config_version(config)
                
                return config
        else:
            # Create default config file
            save_config(DEFAULT_CONFIG)
            print(f"Created default configuration file: {CONFIG_FILE}")
            
            # Check for remote updates
            check_config_version(DEFAULT_CONFIG)
            
            return DEFAULT_CONFIG
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Could not load configuration file: {e}")
        print("Using default configuration")
        return DEFAULT_CONFIG

def save_config(config: Dict) -> None:
    """Save configuration to JSON file with compact formatting."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            # Custom JSON formatting to match example style
            f.write('{\n')
            
            # Write metadata
            f.write('  "metadata": {\n')
            metadata = config.get("metadata", {})
            metadata_items = []
            for key, value in metadata.items():
                if isinstance(value, str):
                    metadata_items.append(f'    "{key}": "{value}"')
                else:
                    metadata_items.append(f'    "{key}": {str(value).lower()}')
            f.write(',\n'.join(metadata_items))
            f.write('\n  },\n')
            
            # Write categories
            f.write('  "categories": {\n')
            categories = config.get("categories", {})
            category_items = []
            
            for category_name, category_data in categories.items():
                extensions = category_data.get("extensions", [])
                folder_name = category_data.get("folder_name", category_name)
                subcategories = category_data.get("subcategories", {})
                
                # Format extensions as a compact array
                extensions_str = ', '.join([f'"{ext}"' for ext in extensions])
                
                category_str = f'    "{category_name}": {{\n      "extensions": [{extensions_str}],\n      "folder_name": "{folder_name}"'
                
                # Add subcategories if they exist
                if subcategories:
                    category_str += ',\n      "subcategories": {'
                    subcategory_items = []
                    for subcat_name, subcat_data in subcategories.items():
                        subcat_folder = subcat_data.get("folder_name", subcat_name)
                        patterns = subcat_data.get("patterns", [])
                        exif_indicators = subcat_data.get("exif_indicators", [])
                        subcat_extensions = subcat_data.get("extensions", [])
                        
                        subcat_str = f'\n        "{subcat_name}": {{\n          "folder_name": "{subcat_folder}"'
                        
                        if patterns:
                            patterns_str = ', '.join([f'"{pattern}"' for pattern in patterns])
                            subcat_str += f',\n          "patterns": [{patterns_str}]'
                        
                        if exif_indicators:
                            indicators_str = ', '.join([f'"{indicator}"' for indicator in exif_indicators])
                            subcat_str += f',\n          "exif_indicators": [{indicators_str}]'
                        
                        if subcat_extensions:
                            subcat_ext_str = ', '.join([f'"{ext}"' for ext in subcat_extensions])
                            subcat_str += f',\n          "extensions": [{subcat_ext_str}]'
                        
                        subcat_str += '\n        }'
                        subcategory_items.append(subcat_str)
                    
                    category_str += ','.join(subcategory_items)
                    category_str += '\n      }'
                
                category_str += '\n    }'
                category_items.append(category_str)
            
            f.write(',\n'.join(category_items))
            f.write('\n  }\n}')
            
    except OSError as e:
        print(f"Warning: Could not save configuration file: {e}")

def update_config_with_defaults(existing_config: Dict) -> Dict:
    """Update existing config with new default categories while preserving user customizations."""
    from datetime import datetime
    
    # Get existing categories
    existing_categories = existing_config.get("categories", {})
    default_categories = DEFAULT_CONFIG.get("categories", {})
    
    # Track changes
    added_categories = []
    updated_categories = []
    
    # Create new config starting with existing one
    updated_config = existing_config.copy()
    
    # Update metadata
    updated_config["metadata"] = {
        "version": DEFAULT_CONFIG.get("metadata", {}).get("version", "1.0"),
        "auto_generated": True,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "last_auto_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": "This is the default configuration - set auto_generated to false to prevent automatic updates"
    }
    
    # Merge categories
    merged_categories = existing_categories.copy()
    
    for category_name, default_category in default_categories.items():
        if category_name not in existing_categories:
            # Add new default category
            merged_categories[category_name] = default_category
            added_categories.append(category_name)
        else:
            # Check if default category has new extensions
            existing_extensions = set(existing_categories[category_name].get("extensions", []))
            default_extensions = set(default_category.get("extensions", []))
            
            if default_extensions - existing_extensions:
                # Add new extensions to existing category
                merged_categories[category_name]["extensions"] = list(
                    existing_extensions | default_extensions
                )
                updated_categories.append(category_name)
    
    updated_config["categories"] = merged_categories
    
    # Print summary of changes
    if added_categories:
        print(f"Added new categories: {', '.join(added_categories)}")
    if updated_categories:
        print(f"Updated categories with new extensions: {', '.join(updated_categories)}")
    
    return updated_config

def get_extension_mapping(config: Dict) -> Dict[str, str]:
    """Create a mapping from file extensions to category folder names."""
    extension_map = {}
    
    for category_name, category_data in config.get("categories", {}).items():
        folder_name = category_data.get("folder_name", category_name)
        extensions = category_data.get("extensions", [])
        
        for ext in extensions:
            extension_map[ext.lower()] = folder_name
    
    return extension_map

def load_ignore_patterns() -> List[str]:
    """Load ignore patterns from .sortignore file."""
    patterns = []
    try:
        if IGNORE_FILE.is_file():
            # Use UTF-8 encoding explicitly to handle special characters
            content = IGNORE_FILE.read_text(encoding='utf-8')
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                patterns.append(line)
    except (UnicodeDecodeError, OSError) as e:
        print(f"Warning: Could not read .sortignore file: {e}")
    return patterns

def should_ignore(name: str, patterns: List[str]) -> bool:
    """Check if a file should be ignored based on patterns."""
    try:
        return any(fnmatch.fnmatch(name, pat) for pat in patterns)
    except Exception:
        # If pattern matching fails, don't ignore the file
        return False

def categorize(ext: str, extension_map: Dict[str, str]) -> str:
    """Categorize file based on extension using the config mapping."""
    ext = ext.lower()
    return extension_map.get(ext, 'Miscellaneous')

def ensure_dir(path: Path) -> Path:
    """Create directory if it doesn't exist."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except (OSError, PermissionError) as e:
        print(f"Error: Could not create directory {path}: {e}")
        raise

def unique_path(dest: Path) -> Path:
    """Generate a unique path for the destination file."""
    if not dest.exists():
        return dest
    
    stem, suffix, parent = dest.stem, dest.suffix, dest.parent
    i = 1
    max_attempts = 1000  # Prevent infinite loops
    
    while i <= max_attempts:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1
    
    # If we've tried 1000 times, just append a timestamp
    import time
    timestamp = int(time.time())
    return parent / f"{stem}_{timestamp}{suffix}"

def safe_move_file(source: Path, dest: Path) -> bool:
    """Safely move a file with error handling."""
    try:
        # Check if source exists and is accessible
        if not source.exists():
            print(f"Warning: Source file {source} does not exist")
            return False
        
        if not source.is_file():
            print(f"Warning: {source} is not a file")
            return False
        
        # Check if we have read permissions
        if not os.access(source, os.R_OK):
            print(f"Warning: No read permission for {source}")
            return False
        
        # Check if destination directory is writable
        if not os.access(dest.parent, os.W_OK):
            print(f"Warning: No write permission for destination directory {dest.parent}")
            return False
        
        # Perform the move
        shutil.move(str(source), str(dest))
        return True
        
    except (OSError, PermissionError) as e:
        print(f"Error moving {source} to {dest}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error moving {source} to {dest}: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are available."""
    required_modules = {
        'fnmatch': 'File name pattern matching',
        'shutil': 'High-level file operations',
        'os': 'Operating system interface',
        'sys': 'System-specific parameters',
        'json': 'JSON encoder/decoder',
        'pathlib': 'Object-oriented filesystem paths',
        'typing': 'Type hints support',
        'subprocess': 'Subprocess management',
        'time': 'Time access and conversions',
        'datetime': 'Date and time types',
        'itertools': 'Iterator functions',
        'PIL': 'Image processing (Pillow)'
    }
    
    missing_modules = []
    
    for module, description in required_modules.items():
        try:
            if module == 'pathlib':
                import pathlib
            elif module == 'typing':
                import typing
            elif module == 'datetime':
                import datetime
            elif module == 'itertools':
                import itertools
            elif module == 'PIL':
                import PIL.Image
                import PIL.ExifTags
            else:
                __import__(module)
        except ImportError as e:
            missing_modules.append(f"{module} ({description}): {e}")
    
    if missing_modules:
        print("Error: Missing required dependencies:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nThese are standard library modules that should be available with Python 3.6+.")
        print("Please ensure you have a complete Python installation.")
        return False
    
    return True

def analyze_image_metadata(image_path: Path) -> Dict:
    """Extract and analyze image metadata for categorization."""
    metadata = {
        'is_screenshot': False,
        'software_used': None,
        'camera_info': None,
        'creation_date': None,
        'resolution': None,
        'color_profile': None
    }
    
    try:
        import PIL.Image
        import PIL.ExifTags
        
        with PIL.Image.open(image_path) as img:
            # Extract EXIF data
            exif = img._getexif()
            if exif:
                # Check for software tags
                software = exif.get(305)  # Software tag
                if software:
                    metadata['software_used'] = software
                
                # Check for camera info
                make = exif.get(271)  # Make tag
                model = exif.get(272)  # Model tag
                if make or model:
                    metadata['camera_info'] = f"{make} {model}".strip()
                
                # Check creation date
                date_original = exif.get(36867)  # DateTimeOriginal tag
                if date_original:
                    metadata['creation_date'] = date_original
            
            # Get image properties
            metadata['resolution'] = img.size
            metadata['color_profile'] = img.mode
            
    except ImportError:
        print("Warning: Pillow not available, image metadata analysis disabled")
    except Exception as e:
        print(f"Warning: Could not analyze {image_path}: {e}")
    
    return metadata

def is_screenshot(filename: str, metadata: Dict) -> bool:
    """Determine if an image is likely a screenshot."""
    # Check filename patterns - only the most reliable ones
    screenshot_patterns = [
        r'Screenshot.*\.(png|jpg|jpeg)$',
        r'Screen Shot.*\.(png|jpg|jpeg)$'
    ]
    
    for pattern in screenshot_patterns:
        if re.match(pattern, filename, re.IGNORECASE):
            return True
    
    # Check metadata indicators
    if metadata['software_used']:
        screenshot_software = ['Screenshot', 'Grab', 'Preview', 'Snipping Tool']
        if any(software.lower() in metadata['software_used'].lower() for software in screenshot_software):
            return True
    
    return False

def categorize_image_subfolder(image_path: Path, metadata: Dict) -> str:
    """Determine the appropriate subfolder for an image."""
    filename = image_path.name
    
    # Check for design files first (by extension)
    design_extensions = ['.psd', '.ai', '.eps', '.sketch', '.fig']
    if image_path.suffix.lower() in design_extensions:
        return "Design Files"
    
    # Check for RAW photos
    raw_extensions = ['.raw', '.dng', '.cr2', '.nef', '.arw', '.orf']
    if image_path.suffix.lower() in raw_extensions:
        return "RAW Photos"
    
    # Check for screenshots
    if is_screenshot(filename, metadata):
        return "Screenshots"
    
    # Check for Adobe-edited images
    if metadata['software_used']:
        adobe_software = ['Adobe Photoshop', 'Adobe Lightroom', 'Adobe Camera Raw', 'Adobe']
        if any(software.lower() in metadata['software_used'].lower() for software in adobe_software):
            return "Adobe Edited"
    
    # Check for camera photos
    if metadata['camera_info']:
        return "Camera Photos"
    
    # Check for web downloads
    web_patterns = [r'^image\d*\.', r'^img\d*\.', r'^photo\d*\.']
    for pattern in web_patterns:
        if re.match(pattern, filename, re.IGNORECASE):
            return "Web Downloads"
    
    # Default to general images
    return "General"

def categorize_with_subfolders(file_path: Path, extension_map: Dict, config: Dict) -> Tuple[str, str]:
    """Categorize file and determine subfolder if applicable."""
    ext = file_path.suffix.lower()
    main_category = extension_map.get(ext, 'Miscellaneous')
    
    # Check if this category has subcategories
    category_config = config.get("categories", {}).get(main_category, {})
    subcategories = category_config.get("subcategories", {})
    
    if not subcategories:
        return main_category, ""
    
    # For images, perform detailed analysis
    if main_category == "Images":
        metadata = analyze_image_metadata(file_path)
        subfolder = categorize_image_subfolder(file_path, metadata)
        return main_category, subfolder
    
    return main_category, ""

def configuration_wizard():
    """Interactive configuration wizard for easy customization."""
    print("\n🔧 Configuration Wizard")
    print("=" * 40)
    print("This wizard helps you customize AutoSort settings.")
    print()
    
    config = load_config()
    
    while True:
        print("Configuration Options:")
        print("1. View current categories")
        print("2. Add new category")
        print("3. Edit existing category")
        print("4. Manual update from defaults")
        print("5. Reset to defaults")
        print("6. Back to main menu")
        print()
        
        try:
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == "1":
                view_categories(config)
            elif choice == "2":
                config = add_new_category(config)
            elif choice == "3":
                config = edit_category(config)
            elif choice == "4":
                config = manual_update_from_defaults(config)
            elif choice == "5":
                config = reset_to_defaults()
            elif choice == "6":
                save_config(config)
                print("✅ Configuration saved!")
                return
            else:
                print("Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\nConfiguration wizard cancelled.")
            return
        except Exception as e:
            print(f"Error: {e}")

def view_categories(config):
    """Display current categories in a readable format."""
    print("\n📋 Current Categories:")
    print("-" * 50)
    
    # Show configuration status
    auto_generated = config.get("metadata", {}).get("auto_generated", False)
    version = config.get("metadata", {}).get("version", "unknown")
    last_modified = config.get("metadata", {}).get("last_modified", "N/A")
    
    if auto_generated:
        print(f"🔄 Auto-generated configuration (v{version})")
        print("   Use 'Manual update from defaults' to get new categories/extensions")
    else:
        print(f"✏️  User-modified configuration (v{version})")
        if last_modified != "N/A":
            print(f"   Last modified: {last_modified}")
        print("   Auto-updates disabled to preserve your customizations")
    
    print()
    
    categories = config.get("categories", {})
    for i, (name, data) in enumerate(categories.items(), 1):
        extensions = data.get("extensions", [])
        folder_name = data.get("folder_name", name)
        print(f"{i:2d}. {name}")
        print(f"    📁 Folder: {folder_name}")
        print(f"    📄 Extensions: {', '.join(extensions[:5])}{'...' if len(extensions) > 5 else ''}")
        
        # Show subcategories if they exist
        subcategories = data.get("subcategories", {})
        if subcategories:
            print(f"    📂 Subcategories: {', '.join(subcategories.keys())}")
        print()

def add_new_category(config):
    """Add a new category through interactive prompts."""
    print("\n➕ Add New Category")
    print("-" * 30)
    
    # Get category name
    while True:
        name = input("Category name (e.g., 'MyFiles'): ").strip()
        if name and name not in config.get("categories", {}):
            break
        elif name in config.get("categories", {}):
            print("❌ Category already exists!")
        else:
            print("❌ Please enter a valid name!")
    
    # Get folder name
    folder_name = input(f"Folder name (default: {name}): ").strip()
    if not folder_name:
        folder_name = name
    
    # Get extensions
    print("Enter file extensions (including the dot, e.g., .txt, .pdf)")
    print("Press Enter twice when done:")
    extensions = []
    while True:
        ext = input(f"Extension {len(extensions)+1}: ").strip()
        if not ext:
            break
        if not ext.startswith('.'):
            ext = '.' + ext
        extensions.append(ext.lower())
    
    # Add to config
    if "categories" not in config:
        config["categories"] = {}
    
    config["categories"][name] = {
        "extensions": extensions,
        "folder_name": folder_name
    }
    
    # Set auto_generated to false since user made changes
    if "metadata" not in config:
        config["metadata"] = {}
    config["metadata"]["auto_generated"] = False
    config["metadata"]["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"✅ Added category '{name}' with {len(extensions)} extensions")
    print("📝 Configuration marked as user-modified (auto-updates disabled)")
    return config

def edit_category(config):
    """Edit an existing category."""
    categories = list(config.get("categories", {}).keys())
    
    if not categories:
        print("❌ No categories to edit!")
        return config
    
    print("\n✏️  Edit Category")
    print("-" * 20)
    
    # Show categories
    for i, name in enumerate(categories, 1):
        print(f"{i}. {name}")
    
    try:
        choice = int(input(f"\nSelect category (1-{len(categories)}): ")) - 1
        if 0 <= choice < len(categories):
            category_name = categories[choice]
            config = edit_specific_category(config, category_name)
        else:
            print("❌ Invalid selection!")
    except ValueError:
        print("❌ Please enter a number!")
    
    return config

def edit_specific_category(config, category_name):
    """Edit a specific category's properties."""
    category = config["categories"][category_name]
    
    print(f"\n✏️  Editing '{category_name}'")
    print("-" * 30)
    
    while True:
        print(f"1. Change folder name (current: {category['folder_name']})")
        print("2. Add extensions")
        print("3. Remove extensions")
        print("4. Back")
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            new_name = input("New folder name: ").strip()
            if new_name:
                category["folder_name"] = new_name
                # Set auto_generated to false since user made changes
                if "metadata" not in config:
                    config["metadata"] = {}
                config["metadata"]["auto_generated"] = False
                config["metadata"]["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("✅ Folder name updated!")
                print("📝 Configuration marked as user-modified (auto-updates disabled)")
        
        elif choice == "2":
            ext = input("Extension to add (including dot): ").strip()
            if ext and not ext.startswith('.'):
                ext = '.' + ext
            if ext and ext not in category["extensions"]:
                category["extensions"].append(ext.lower())
                # Set auto_generated to false since user made changes
                if "metadata" not in config:
                    config["metadata"] = {}
                config["metadata"]["auto_generated"] = False
                config["metadata"]["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("✅ Extension added!")
                print("📝 Configuration marked as user-modified (auto-updates disabled)")
            else:
                print("❌ Invalid or duplicate extension!")
        
        elif choice == "3":
            extensions = category["extensions"]
            if extensions:
                print("Current extensions:")
                for i, ext in enumerate(extensions, 1):
                    print(f"  {i}. {ext}")
                try:
                    idx = int(input("Enter number to remove: ")) - 1
                    if 0 <= idx < len(extensions):
                        removed = extensions.pop(idx)
                        # Set auto_generated to false since user made changes
                        if "metadata" not in config:
                            config["metadata"] = {}
                        config["metadata"]["auto_generated"] = False
                        config["metadata"]["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"✅ Removed {removed}")
                        print("📝 Configuration marked as user-modified (auto-updates disabled)")
                    else:
                        print("❌ Invalid selection!")
                except ValueError:
                    print("❌ Please enter a number!")
            else:
                print("❌ No extensions to remove!")
        
        elif choice == "4":
            break
    
    return config

def manual_update_from_defaults(config):
    """Manually update configuration from defaults with conflict resolution."""
    print("\n🔄 Manual Update from Defaults")
    print("-" * 35)
    print("This will merge new default categories and extensions with your current configuration.")
    print("Conflicts will be resolved by keeping your customizations.")
    print()
    
    # Check if config is already auto-generated
    auto_generated = config.get("metadata", {}).get("auto_generated", False)
    if auto_generated:
        print("ℹ️  Your configuration is already auto-generated. No manual update needed.")
        return config
    
    # Show what will be updated
    default_categories = DEFAULT_CONFIG.get("categories", {})
    current_categories = config.get("categories", {})
    
    new_categories = []
    updated_categories = []
    
    for category_name, default_category in default_categories.items():
        if category_name not in current_categories:
            new_categories.append(category_name)
        else:
            # Check for new extensions
            current_extensions = set(current_categories[category_name].get("extensions", []))
            default_extensions = set(default_category.get("extensions", []))
            new_extensions = default_extensions - current_extensions
            if new_extensions:
                updated_categories.append(f"{category_name} (+{len(new_extensions)} extensions)")
    
    if not new_categories and not updated_categories:
        print("✅ Your configuration is up to date!")
        return config
    
    print("📋 Changes that will be applied:")
    if new_categories:
        print(f"  New categories: {', '.join(new_categories)}")
    if updated_categories:
        print(f"  Updated categories: {', '.join(updated_categories)}")
    
    print()
    confirm = input("Apply these updates? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        # Perform the update
        updated_config = update_config_with_defaults(config)
        
        # Keep auto_generated as false since this was a manual update
        if "metadata" not in updated_config:
            updated_config["metadata"] = {}
        updated_config["metadata"]["auto_generated"] = False
        updated_config["metadata"]["last_manual_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("✅ Manual update completed!")
        print("📝 Configuration remains user-modified (auto-updates disabled)")
        return updated_config
    else:
        print("❌ Manual update cancelled.")
        return config

def reset_to_defaults():
    """Reset configuration to defaults."""
    print("\n⚠️  Reset to Defaults")
    print("-" * 25)
    confirm = input("This will overwrite your current configuration. Continue? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        print("✅ Configuration reset to defaults!")
        print("🔄 Auto-updates re-enabled for default configuration")
        return DEFAULT_CONFIG
    else:
        print("❌ Reset cancelled.")
        return load_config()

def analyze_files(files_to_process, extension_map, config):
    """Analyze files and provide statistics before processing."""
    print("\n📊 File Analysis")
    print("-" * 30)
    
    # Count by category
    category_counts = {}
    category_sizes = {}
    total_size = 0
    
    for item in files_to_process:
        category, subfolder = categorize_with_subfolders(item, extension_map, config)
        
        # Count files
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1
        
        # Calculate sizes
        try:
            size = item.stat().st_size
            total_size += size
            
            if category not in category_sizes:
                category_sizes[category] = 0
            category_sizes[category] += size
        except OSError:
            pass  # Skip files we can't access
    
    # Display statistics
    print(f"📁 Total files: {len(files_to_process)}")
    print(f"💾 Total size: {format_size(total_size)}")
    print()
    
    print("📋 Files by category:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        size = category_sizes.get(category, 0)
        print(f"  {category}: {count} files ({format_size(size)})")
    
    return category_counts, category_sizes

def format_size(size_bytes):
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def show_detailed_errors(error_log):
    """Show detailed error information if any occurred."""
    if not error_log:
        return
    
    print("\n⚠️  Error Summary")
    print("-" * 20)
    
    error_types = {}
    for error in error_log:
        error_type = type(error).__name__
        if error_type not in error_types:
            error_types[error_type] = []
        error_types[error_type].append(str(error))
    
    for error_type, messages in error_types.items():
        print(f"\n{error_type} ({len(messages)} occurrences):")
        for msg in messages[:3]:  # Show first 3 examples
            print(f"  • {msg}")
        if len(messages) > 3:
            print(f"  ... and {len(messages) - 3} more")

def main():
    """Main function with improved error handling."""
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Load configuration and check version before menu
    print("📋 Loading configuration...")
    config = load_config()
    
    # Get source directory and target root from user
    source_dir, target_root, dry_run = get_source_directory()
    
    print(f"Source directory: {source_dir}")
    print(f"Target root: {target_root}")
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be moved")
    
    # Check if source directory exists
    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} does not exist")
        sys.exit(1)
    
    if not source_dir.is_dir():
        print(f"Error: {source_dir} is not a directory")
        sys.exit(1)
    
    # Get extension mapping from already loaded config
    extension_map = get_extension_mapping(config)
    
    # Display loaded categories
    categories = config.get("categories", {})
    print(f"✅ Loaded {len(categories)} categories from configuration")
    
    # Load ignore patterns
    patterns = load_ignore_patterns()
    if patterns:
        print(f"🚫 Loaded {len(patterns)} ignore patterns")
    
    # Count files to process
    print("🔍 Scanning files...")
    files_to_process = []
    for item in source_dir.iterdir():
        if (item.is_file() and 
            not should_ignore(item.name, patterns) and
            item.name != 'autosort.py' and 
            item.name != 'autosort_config.json' and 
            item != target_root):
            files_to_process.append(item)
    
    if not files_to_process:
        print("✨ No files found to organize!")
        return
    
    print(f"📁 Found {len(files_to_process)} files to organize")
    
    # Process files
    moved_count = 0
    error_count = 0
    error_log = []
    
    # Show file analysis
    if not dry_run:
        analyze_files(files_to_process, extension_map, config)
    
    print("\n🔄 Starting organization...")
    for i, item in enumerate(files_to_process, 1):
        try:
            # Show progress
            progress = (i / len(files_to_process)) * 100
            print(f"\r📊 Progress: {progress:.1f}% ({i}/{len(files_to_process)})", end="", flush=True)
            
            # Categorize with subfolder support
            category, subfolder = categorize_with_subfolders(item, extension_map, config)
            
            # Create directory structure
            if subfolder:
                cat_dir = ensure_dir(target_root / category / subfolder)
            else:
                cat_dir = ensure_dir(target_root / category)
            
            dest = unique_path(cat_dir / item.name)
            
            if dry_run:
                if subfolder:
                    print(f"\n  📄 Would move '{item.name}' → '{category}/{subfolder}/'")
                else:
                    print(f"\n  📄 Would move '{item.name}' → '{category}/'")
            else:
                if safe_move_file(item, dest):
                    if subfolder:
                        print(f"\n  ✅ Moved '{item.name}' → '{category}/{subfolder}/'")
                    else:
                        print(f"\n  ✅ Moved '{item.name}' → '{category}/'")
                    moved_count += 1
                else:
                    print(f"\n  ❌ Failed to move '{item.name}'")
                    error_count += 1
                    error_log.append(f"Failed to move {item.name}")
                    
        except Exception as e:
            print(f"\n  ⚠️  Error processing {item}: {e}")
            error_count += 1
            error_log.append(f"Error processing {item}: {e}")
    
    print()  # New line after progress
    
    # Show detailed errors if any
    if error_log and not dry_run:
        show_detailed_errors(error_log)
    
    # Summary
    if dry_run:
        print(f"\n📋 Preview Summary: {len(files_to_process)} files would be organized")
        print("💡 Run the script again and choose option 1, 2, or 3 to actually move the files")
    else:
        print(f"\n🎉 Summary: {moved_count} files moved, {error_count} errors")
        if moved_count > 0:
            print(f"📁 Files organized in: {target_root}")
            print("✨ Your files are now organized!")

if __name__ == '__main__':
    main()
