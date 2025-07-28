# AutoSort - Desktop File Organizer

A Python script that automatically organizes files on your Desktop into categorized folders.

## Features

- **Automatic Categorization**: Files are sorted into categories based on their file extensions
- **Configurable Categories**: Customize categories, file types, and folder names via JSON configuration
- **Cross-platform Desktop Detection**: Works with different locale Desktop folder names (Desktop, Escritorio, Bureau, etc.)
- **Safe File Handling**: Prevents overwriting files and handles naming conflicts
- **Ignore Patterns**: Support for `.sortignore` file to exclude specific files
- **Comprehensive File Types**: Supports images, audio, video, documents, code, archives, and more

## Supported File Categories

- **Images**: JPG, JPEG 2000 (JP2, J2K, JPF, JPX), PNG, GIF, BMP, TIFF/TIF, HEIC, RAW/CR2/NEF/ARW/ORF/DNG, SVG, WebP, AVIF, JXL, PSD, AI, EPS, ICO, ICNS, TGA, WebP
- **Audio**: MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, AMR, WMA, AIFF, ALAC, MIDI/MID, WV, RA, APE, DTS
- **Video**: MP4, MOV, AVI, MKV, FLV, WMV, WebM, M4V, 3GP, MPEG/MPG, TS, M2TS, MTS, DIVX, OGV, VOB, RM, ASF, MXF, H264, HEVC/H265
- **Documents**: PDF, DOC/DOCX, PPT/PPTX, XLS/XLSX, ODT, ODS, ODP, Pages, Key, Numbers
- **Code**: Python (.py), JavaScript/TypeScript (.js/.ts/.jsx/.tsx), Shell (.sh), Ruby (.rb), Perl (.pl), C/C++ (.c/.cpp/.h), C# (.cs), Java (.java), Go (.go), Rust (.rs), PHP (.php), Swift (.swift), Kotlin (.kt), Scala (.scala), Dart (.dart), R (.r), Objective-C (.m), Lua (.lua), HTML (.html/.htm), CSS/SCSS/LESS (.css/.scss/.less), Vue (.vue), Svelte (.svelte), SQL (.sql), PowerShell (.ps1)
- **Text**: TXT, Markdown (.md/.markdown), RTF, LOG, CSV, TEX, JSON, XML, YAML/YML, INI, CFG, CONF, TOML, AsciiDoc (.adoc/.asciidoc), reStructuredText (.rst), PROPERTIES
- **Archives**: ZIP, RAR, 7Z, TAR, TGZ, TAR.GZ, TAR.BZ2, TAR.XZ, GZ, BZ2, XZ, ZST/ZSTD, LZ, LZMA, CAB, ACE, ARJ
- **eBooks**: EPUB, MOBI, AZW, AZW3, FB2
- **Fonts**: TTF, OTF, WOFF, WOFF2, FNT
- **Special Categories**: Minecraft files, Non-Mac/Windows executables (EXE, MSI, DLL, COM, BAT, CMD, SYS, SCR, APK, DEB, RPM, PKG), Disk images (DMG, ISO, IMG, VHD/VHDX, VMDK, QCOW2, BIN, TOAST), Reaper projects, Music scores, 3D models

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

### Custom Categories with autosort_config.json

The script now uses a JSON configuration file (`autosort_config.json`) that allows you to customize categories, file extensions, and folder names without modifying the script.

#### Configuration File Structure

The configuration file contains:

**Metadata Section:**
- `version`: Configuration version
- `auto_generated`: Boolean flag indicating if this config should be auto-updated
- `last_updated`: Date when the config was last updated
- `last_auto_update`: Timestamp of the last automatic update (added automatically)

**Categories Section:**
Each category has:
- `extensions`: Array of file extensions (including the dot)
- `folder_name`: The name of the folder where files will be sorted

#### Example Configuration

```json
{
  "categories": {
    "MyCustomCategory": {
      "extensions": [".myfile", ".custom", ".special"],
      "folder_name": "My Custom Files"
    },
    "Images": {
      "extensions": [".jpg", ".png", ".gif"],
      "folder_name": "Images"
    }
  }
}
```

#### Adding New Categories

1. Open `autosort_config.json` in a text editor
2. Add a new category object with your desired extensions and folder name
3. Save the file and run the script

#### Modifying Existing Categories

You can:
- Add new file extensions to existing categories
- Remove file extensions from categories
- Change folder names for categories
- Reorder categories (order doesn't matter)

#### Default Configuration

If no `autosort_config.json` file exists, the script will create one with default categories including Images, Audio, Video, Documents, Code, Archives, and more.

#### Automatic Updates

The configuration file includes metadata that tracks whether it was auto-generated. When `auto_generated` is set to `true`, the script will automatically:

- Add new default categories that don't exist in your configuration
- Add new file extensions to existing default categories
- Update the `last_auto_update` timestamp

This ensures your configuration stays up-to-date with new features and file types without losing your custom categories.

To prevent automatic updates, set `auto_generated` to `false` in the metadata section:

```json
{
  "metadata": {
    "version": "1.0",
    "auto_generated": false,
    "last_updated": "2024-01-01"
  }
}
```

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

## How It Works

1. The script detects your Desktop directory (supports multiple locales)
2. Loads the configuration from `autosort_config.json` (creates default if not exists)
3. Creates an `Autosort` folder on your Desktop
4. Scans all files on your Desktop (excluding those in `.sortignore`)
5. Categorizes each file based on its extension using the configuration
6. Moves files to appropriate subfolders within `Autosort`
7. Handles naming conflicts by appending numbers or timestamps

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that allows others to use, modify, and distribute your code with very few restrictions. It's one of the most popular open source licenses due to its simplicity and permissiveness.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the script. 