# AutoSort - Desktop File Organizer

A Python script that automatically organizes files on your Desktop into categorized folders.

## Features

- **Automatic Categorization**: Files are sorted into categories based on their file extensions
- **Cross-platform Desktop Detection**: Works with different locale Desktop folder names (Desktop, Escritorio, Bureau, etc.)
- **Safe File Handling**: Prevents overwriting files and handles naming conflicts
- **Ignore Patterns**: Support for `.sortignore` file to exclude specific files
- **Comprehensive File Types**: Supports images, audio, video, documents, code, archives, and more

## Supported File Categories

- **Images**: JPG, PNG, GIF, BMP, TIFF, HEIC, RAW, SVG, WebP, PSD, AI, EPS, ICO
- **Audio**: MP3, WAV, FLAC, AAC, M4A, OGG, WMA, AIFF, ALAC
- **Video**: MP4, MOV, AVI, MKV, FLV, WMV, WebM, M4V, 3GP, MPEG, MPG
- **Documents**: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, Pages, Key, Numbers
- **Code**: Python, JavaScript, Shell, Ruby, Perl, C/C++, Java, Go, Rust, TypeScript, PHP, Swift, Kotlin, Scala, PowerShell
- **Text**: TXT, MD, RTF, LOG, CSV, TEX, JSON, XML, YAML, INI, CFG, CONF
- **Archives**: ZIP, RAR, 7Z, TAR, GZ, BZ2, XZ
- **Special Categories**: Minecraft files, Non-Mac files, Disk images, Reaper projects, Music scores, 3D models

## Installation

1. Clone or download this repository
2. Ensure you have Python 3.6+ installed
3. No additional dependencies required

## Usage

### Command Line
```bash
python3 autosort.py
```

### macOS Double-Click
Double-click the `run-autosort.command` file to execute the script.

## Configuration

### Ignoring Files with .sortignore

Create a `.sortignore` file in the same directory as the script to specify files and folders that should not be moved during the sorting process.

#### .sortignore File Format

The `.sortignore` file uses simple pattern matching:
- One pattern per line
- Lines starting with `#` are treated as comments
- Supports wildcards (`*`) for matching multiple files
- Supports exact file names

#### Example .sortignore File

```
# System files
.DS_Store
Thumbs.db
desktop.ini

# Temporary files
*.tmp
*.temp
temp_*
~*

# Specific files to keep on Desktop
important_document.pdf
my_project/

# File patterns
*.log
backup_*
```

#### How .sortignore Works

- Files matching any pattern in `.sortignore` will remain on your Desktop
- The script reads the `.sortignore` file before starting the sorting process
- If no `.sortignore` file exists, all files will be processed normally
- The file is case-sensitive on most systems

### Custom Categories
You can modify the extension sets in the script to add or remove file types from categories.

## How It Works

1. The script detects your Desktop directory (supports multiple locales)
2. Creates an `Autosort` folder on your Desktop
3. Scans all files on your Desktop (excluding those in `.sortignore`)
4. Categorizes each file based on its extension
5. Moves files to appropriate subfolders within `Autosort`
6. Handles naming conflicts by appending numbers or timestamps

## Safety Features

- **No Overwriting**: Files with duplicate names get unique names
- **Permission Checks**: Verifies read/write permissions before moving files
- **Error Handling**: Graceful handling of permission errors and file access issues
- **Dry Run**: Consider testing on a small set of files first

## Requirements

- Python 3.6+
- macOS (for Desktop path detection)
- Read/write permissions on Desktop directory

## License

This project is open source. Feel free to modify and distribute as needed.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the script. 