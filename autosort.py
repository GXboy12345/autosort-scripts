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
from pathlib import Path
from typing import List, Dict, Set

# —— Configuration —— #
SCRIPT_DIR   = Path(__file__).resolve().parent
IGNORE_FILE  = SCRIPT_DIR / '.sortignore'
CONFIG_FILE  = SCRIPT_DIR / 'autosort_config.json'

# Default configuration
DEFAULT_CONFIG = {
    "metadata": {
        "version": "1.11",
        "auto_generated": True,
        "last_updated": "2025-08-06",
        "note": "This is the default configuration - set auto_generated to false to prevent automatic updates"
    },
    "categories": {
        "Images": {
            "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".heic", ".raw", ".svg", ".webp", ".psd", ".ai", ".eps", ".ico", ".avif", ".jxl", ".jp2", ".j2k", ".jpf", ".jpx", ".tga", ".dng", ".cr2", ".nef", ".orf", ".arw", ".icns"],
            "folder_name": "Images"
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
        "Reaper": {
            "extensions": [".rpp", ".rpl", ".rpreset", ".rpp.gz", ".rpp.bz2", ".rpp.xz", ".rpp.tar", ".rpp.tar.gz", ".rpp.tar.bz2", ".rpp.tar.xz"],
            "folder_name": "Reaper Projects"
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
            "extensions": [".flp", ".als", ".aup", ".aup3", ".sesx", ".ptx", ".rpp"],
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

def get_source_directory() -> tuple[Path, Path]:
    """Get the source directory and target root based on user choice."""
    desktop_path = get_desktop_path()
    
    print("AutoSort - File Organizer")
    print("=" * 40)
    print(f"1. Organize Desktop ({desktop_path})")
    print("2. Select custom folder")
    print("3. Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == "1":
                source_dir = desktop_path
                target_root = source_dir / 'Autosort'
                print(f"Selected: Desktop ({source_dir})")
                return source_dir, target_root
                
            elif choice == "2":
                print("Opening folder selection dialog...")
                selected_path = select_folder_dialog()
                
                if selected_path:
                    source_dir = selected_path
                    target_root = source_dir / 'Autosort'
                    print(f"Selected: {source_dir}")
                    return source_dir, target_root
                else:
                    print("Please try again or select option 3 to exit.")
                    continue
                    
            elif choice == "3":
                print("Goodbye!")
                sys.exit(0)
                
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
                
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


def load_config() -> Dict:
    """Load configuration from JSON file or create default if not exists."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"Loaded configuration from {CONFIG_FILE}")
                
                # Check version and auto-generated flag
                auto_generated = config.get("metadata", {}).get("auto_generated", False)
                default_version = DEFAULT_CONFIG.get("metadata", {}).get("version", "0")
                config_version = str(config.get("metadata", {}).get("version", "0"))

                if auto_generated and is_version_newer(default_version, config_version):
                    updated_config = update_config_with_defaults(config)
                    if updated_config != config:
                        save_config(updated_config)
                        print(f"Auto-generated config updated from version {config_version} to {default_version} with new default categories")
                        return updated_config
                
                return config
        else:
            # Create default config file
            save_config(DEFAULT_CONFIG)
            print(f"Created default configuration file: {CONFIG_FILE}")
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
                
                # Format extensions as a compact array
                extensions_str = ', '.join([f'"{ext}"' for ext in extensions])
                
                category_str = f'    "{category_name}": {{\n      "extensions": [{extensions_str}],\n      "folder_name": "{folder_name}"\n    }}'
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
        'itertools': 'Iterator functions'
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

def main():
    """Main function with improved error handling."""
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Get source directory and target root from user
    source_dir, target_root = get_source_directory()
    
    print(f"Source directory: {source_dir}")
    print(f"Target root: {target_root}")
    
    # Check if source directory exists
    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} does not exist")
        sys.exit(1)
    
    if not source_dir.is_dir():
        print(f"Error: {source_dir} is not a directory")
        sys.exit(1)
    
    # Load configuration
    config = load_config()
    extension_map = get_extension_mapping(config)
    
    # Display loaded categories
    categories = config.get("categories", {})
    print(f"Loaded {len(categories)} categories from configuration")
    
    # Load ignore patterns
    patterns = load_ignore_patterns()
    if patterns:
        print(f"Loaded {len(patterns)} ignore patterns")
    
    # Process files
    moved_count = 0
    error_count = 0
    
    try:
        for item in source_dir.iterdir():
            try:
                # Skip if not a file or should be ignored
                if not item.is_file() or should_ignore(item.name, patterns):
                    continue
                
                # Skip the script itself, config file, and the target directory
                if (item.name == 'autosort.py' or 
                    item.name == 'autosort_config.json' or 
                    item == target_root):
                    continue
                
                # Categorize and move
                category = categorize(item.suffix, extension_map)
                cat_dir = ensure_dir(target_root / category)
                dest = unique_path(cat_dir / item.name)
                
                if safe_move_file(item, dest):
                    print(f"Moved '{item.name}' → '{category}/'")
                    moved_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                print(f"Error processing {item}: {e}")
                error_count += 1
                
    except Exception as e:
        print(f"Error iterating through source directory: {e}")
        sys.exit(1)
    
    # Summary
    print(f"\nSummary: {moved_count} files moved, {error_count} errors")

if __name__ == '__main__':
    main()
