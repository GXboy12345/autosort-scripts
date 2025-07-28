#!/usr/bin/env python3
"""
AutoSort - Desktop file organizer

This script automatically organizes files on your Desktop into categorized folders.

Requirements:
- Python 3.6+
- macOS (for Desktop path detection)

Copyright (c) 2024 Gboy
Licensed under the MIT License - see LICENSE file for details.
"""

import fnmatch
import shutil
import os
import sys
from pathlib import Path
from typing import List

# —— Configuration —— #
SCRIPT_DIR   = Path(__file__).resolve().parent
IGNORE_FILE  = SCRIPT_DIR / '.sortignore'

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

DESKTOP_DIR  = get_desktop_path()
TARGET_ROOT  = DESKTOP_DIR / 'Autosort'

# Extension sets
IMAGE_EXTS      = {'.jpg','.jpeg','.png','.gif','.bmp','.tiff','.tif','.heic','.raw','.svg','.webp','.psd','.ai','.eps','.ico',
                    '.avif','.jxl','.jp2','.j2k','.jpf','.jpx','.tga','.dng','.cr2','.nef','.orf','.arw','.icns'}
AUDIO_EXTS      = {'.mp3','.wav','.flac','.aac','.m4a','.ogg','.wma','.aiff','.alac','.opus','.amr','.mid','.midi','.wv','.ra','.ape','.dts'}
VIDEO_EXTS      = {'.mp4','.mov','.avi','.mkv','.flv','.wmv','.webm','.m4v','.3gp','.mpeg','.mpg','.ts','.m2ts','.mts','.m2v','.divx','.ogv','.h264','.h265','.hevc','.vob','.rm','.asf','.mxf'}
TEXT_EXTS       = {'.txt','.md','.rtf','.log','.csv','.tex','.json','.xml','.yaml','.yml','.ini','.cfg','.conf','.toml','.adoc','.asciidoc','.rst','.properties'}
ARCHIVE_EXTS    = {'.zip','.rar','.7z','.tar','.gz','.bz2','.xz','.tgz','.tar.gz','.tar.bz2','.tar.xz','.zst','.zstd','.lz','.lzma','.cab','.ace','.arj'}
MINECRAFT_EXTS  = {'.jar','.schem','.schematic','.litematic','.nbt', '.mcfunction'}
NONMAC_EXTS     = {'.exe','.msi','.dll','.com','.bat','.cmd','.sys','.apk','.appimage','.scr','.deb','.rpm','.cab','.pkg'}
DOCUMENT_EXTS   = {'.pdf','.doc','.docx','.ppt','.pptx','.xls','.xlsx','.pages','.key','.numbers','.odt','.ods','.odp'}
CODE_EXTS       = {'.py','.js','.sh','.rb','.pl','.c','.cpp','.h','.java','.go','.rs','.ts','.jsx','.tsx','.php','.swift','.kt','.kts','.scala','.ps1','.cs','.dart','.r','.m','.lua','.html','.htm','.css','.scss','.less','.vue','.svelte','.sql'}
DISK_EXTS       = {'.dmg','.iso','.img','.bin','.toast','.toast.gz','.toast.bz2','.toast.xz','.toast.tar','.toast.tar.gz','.toast.tar.bz2','.toast.tar.xz','.vhd','.vhdx','.vmdk','.qcow2'}
REAPER_EXTS     = {'.rpp','.rpl','.rpreset','.rpp.gz','.rpp.bz2','.rpp.xz','.rpp.tar','.rpp.tar.gz','.rpp.tar.bz2','.rpp.tar.xz'}
MUSICSCORE_EXTS = {'.mscz','.mscx','.mscx.gz','.mscx.bz2','.mscx.xz','.mscx.tar','.mscx.tar.gz','.mscx.tar.bz2','.mscx.tar.xz'}
THREE_D_EXTS    = {'.stl','.obj','.fbx','.dae','.3ds','.ply','.glb','.gltf','.blend','.3mf','.igs','.iges','.stp','.step'}
EBOOK_EXTS      = {'.epub','.mobi','.azw','.azw3','.fb2'}
FONT_EXTS       = {'.ttf','.otf','.woff','.woff2','.fnt'}

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

def categorize(ext: str) -> str:
    """Categorize file based on extension."""
    ext = ext.lower()
    if ext in IMAGE_EXTS:      return 'Image'
    if ext in AUDIO_EXTS:      return 'Audio'
    if ext in VIDEO_EXTS:      return 'Video'
    if ext in TEXT_EXTS:       return 'Text'
    if ext in DOCUMENT_EXTS:   return 'Documents'
    if ext in CODE_EXTS:       return 'Code'
    if ext in ARCHIVE_EXTS:    return 'Compressed archive'
    if ext in MINECRAFT_EXTS:  return 'Minecraft-related file'
    if ext in NONMAC_EXTS:     return 'Non-mac file'
    if ext in DISK_EXTS:       return 'Disk image'
    if ext in REAPER_EXTS:     return 'Reaper project'
    if ext in MUSICSCORE_EXTS: return 'Music score'
    if ext in THREE_D_EXTS:    return '3D model'
    if ext in EBOOK_EXTS:      return 'eBook'
    if ext in FONT_EXTS:       return 'Fonts'
    return 'Miscellaneous'

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

def main():
    """Main function with improved error handling."""
    print(f"Desktop directory: {DESKTOP_DIR}")
    print(f"Target root: {TARGET_ROOT}")
    
    # Check if Desktop directory exists
    if not DESKTOP_DIR.exists():
        print(f"Error: Desktop directory {DESKTOP_DIR} does not exist")
        sys.exit(1)
    
    if not DESKTOP_DIR.is_dir():
        print(f"Error: {DESKTOP_DIR} is not a directory")
        sys.exit(1)
    
    # Load ignore patterns
    patterns = load_ignore_patterns()
    if patterns:
        print(f"Loaded {len(patterns)} ignore patterns")
    
    # Process files
    moved_count = 0
    error_count = 0
    
    try:
        for item in DESKTOP_DIR.iterdir():
            try:
                # Skip if not a file or should be ignored
                if not item.is_file() or should_ignore(item.name, patterns):
                    continue
                
                # Skip the script itself and the target directory
                if item.name == 'autosort.py' or item == TARGET_ROOT:
                    continue
                
                # Categorize and move
                category = categorize(item.suffix)
                cat_dir = ensure_dir(TARGET_ROOT / category)
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
        print(f"Error iterating through Desktop directory: {e}")
        sys.exit(1)
    
    # Summary
    print(f"\nSummary: {moved_count} files moved, {error_count} errors")

if __name__ == '__main__':
    main()
