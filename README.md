# AutoSort - File Organizer

A Python script that automatically organizes files into categorized folders. Can organize your Desktop or any custom folder you select.

**Current Version**: 2.2 (2025-08-31)

## What's New in v2.2

- **Email Organization**: New Emails category for .eml, .msg, .emlx, and .oft files
- **Calendar Files**: New Calendars category for .ics, .ical, .ifb, and .vcs files
- **Game Files Enhancement**: New Game Files category with Osu and Minecraft subcategories for organized gaming file management
- **Music Scores Expansion**: Added Guitar Pro formats (.gp, .gp3, .gp4, .gp5, .gpx, .gp7) and MusicXML (.musicxml, .mxl) support
- **Minecraft Reorganization**: Minecraft files now organized under Game Files/Minecraft with .litematica support
- **Extensionless Files**: New category for files without extensions with intelligent handling

## Features

- **Flexible Source Selection**: Choose between organizing your Desktop or any custom folder
- **Preview Mode**: See what will happen before moving any files (dry run)
- **Detailed Output**: Visually appealing per-file display showing destination paths
- **File Analysis**: Statistics by category with file counts and sizes
- **Configuration Wizard**: Interactive wizard for adding, editing, and managing categories
- **Graphical Interface**: Both command-line and GUI versions available
- **Automatic Categorization**: Files are sorted into categories based on their file extensions
- **Configurable Categories**: Customize categories, file types, and folder names via JSON configuration
- **Cross-platform Desktop Detection**: Works with different locale Desktop folder names (Desktop, Escritorio, Bureau, etc.)
- **Safe File Handling**: Prevents overwriting files and handles naming conflicts
- **Ignore Patterns**: Support for `.sortignore` file to exclude specific files
- **Comprehensive File Types**: Supports images, audio, video, documents, code, archives, and more
- **Progress Tracking**: Real-time progress indicators and detailed statistics
- **Smart Image Organization**: Advanced image categorization with subfolders
- **Undo Functionality**: Complete undo system with transaction tracking


## Installation

1. Clone or download this repository
2. Ensure you have Python 3.8+ installed
3. Install required dependencies:
   
   **Option A: Automatic Installation (macOS)**
   ```bash
   # Double-click install_dependencies.command
   # OR run from terminal:
   ./install_dependencies.command
   ```
   
   **Option B: Manual Installation**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface
```bash
python3 autosort.py
```

The script will present you with a menu:
1. **Organize Desktop** - Sort files from your Desktop folder
2. **Organize Downloads** - Sort files from your Downloads folder
3. **Organize Custom Folder** - Choose any folder to organize using a folder selection dialog
4. **Preview Desktop Organization** - See what would happen without moving files
5. **Preview Downloads Organization** - See what would happen without moving files
6. **Preview Custom Folder Organization** - See what would happen without moving files
7. **Configuration Wizard** - Customize categories and settings
8. **Undo Last Operation** - Revert the last file organization
q. **Exit** - Quit the application

### Command Line Options
```bash
# Use CLI interface (default)
python3 autosort.py

# Use GUI interface (when available)
python3 autosort.py --gui

# Show help
python3 autosort.py --help
```

### Graphical User Interface
```bash
python3 autosort.py --gui
```

Or double-click the `run-autosort-gui.command` file.

The GUI provides:
- **Visual folder selection** with browse button
- **Quick access buttons** for Desktop and Downloads folders
- **Preview mode checkbox** for safe testing
- **Real-time progress bar** and status updates
- **Detailed log window** showing all operations
- **File analysis** with category breakdowns
- **Easy start/stop controls**
- **Undo functionality** with one-click undo button

- **Threaded operations** for responsive interface

### macOS Double-Click
- **Command Line**: Double-click `run-autosort.command`
- **GUI**: Double-click `run-autosort-gui.command`



## Undo System

AutoSort includes a complete undo system that allows you to revert file organization operations:

### How It Works
- **Transaction-based**: Each organization operation is tracked as a complete transaction
- **Persistent Storage**: Undo history is automatically saved to `autosort_undo.json`
- **Smart Rollback**: Files are moved back to their original locations
- **Conflict Resolution**: Handles cases where original locations are no longer available

### Using Undo
```bash
# From the main menu, select option 8
8. Undo Last Operation
```

### Undo Information
The system shows you what can be undone:
```
↩️  Can undo: Organize Desktop
```

### Undo Process
1. **Confirmation**: You'll be asked to confirm the undo operation
2. **File Restoration**: Files are moved back to their original locations
3. **Conflict Handling**: If a file already exists, it gets a unique name
4. **Status Update**: You'll see the results of the undo operation

### Undo Limitations
- **File Modifications**: If files were modified after organization, they won't be restored
- **Manual Changes**: Files moved manually after organization aren't tracked
- **System Files**: Some system files may not be restorable due to permissions

### Example Undo Session
```
↩️  Undoing: Organize Desktop
Continue? (y/N): y

✅ Operation undone successfully
   Files restored: 45
   Errors: 0
   Original locations preserved
```

## Supported File Categories

The script supports **29+ categories** with comprehensive file type coverage and intelligent subcategorization:

### Core Media Categories
- **Images**: JPG, JPEG 2000 (JP2, J2K, JPF, JPX), PNG, GIF, BMP, TIFF/TIF, HEIC, RAW formats (CR2, NEF, ARW, ORF, DNG), SVG, WebP, AVIF, JXL, PSD, AI, EPS, ICO, ICNS, TGA
  - **Screenshots**: Automatically detected screenshots (macOS, Windows patterns)
  - **Adobe Edited**: Images processed through Adobe software (Photoshop, Lightroom, Camera Raw)
  - **Camera Photos**: Photos taken with digital cameras (identified via EXIF metadata)
  - **Web Downloads**: Images downloaded from the web (common naming patterns)
  - **Design Files**: Professional design files (PSD, AI, EPS, Sketch, Figma)
  - **RAW Photos**: Unprocessed camera RAW files
- **Audio**: MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, AMR, WMA, AIFF, ALAC, MIDI/MID, WV, RA, APE, DTS
  - **Music**: Music files, songs, tracks, albums, and playlists
  - **Podcasts**: Podcast episodes and shows
  - **Voice Recordings**: Voice memos, notes, and interviews
  - **Sound Effects**: SFX, sound effects, and audio files
  - **Audiobooks**: Audiobook files, books, and chapters
- **Video**: MP4, MOV, AVI, MKV, FLV, WMV, WebM, M4V, 3GP, MPEG/MPG, TS, M2TS, MTS, DIVX, OGV, VOB, RM, ASF, MXF, H264, HEVC/H265
  - **Movies**: Movie and film files
  - **TV Shows**: Episodes, seasons, and series
  - **Tutorials**: Tutorial, how-to, guide, lesson, and course videos
  - **Screen Recordings**: Screen captures, recordings, and demos
  - **Home Videos**: Personal, family, vacation, and trip videos

### Document Categories
- **Documents**: PDF, DOC/DOCX, Pages, ODT
  - **PDFs**: PDF documents
  - **Word Documents**: DOC, DOCX, and ODT files
  - **Pages Documents**: Apple Pages files
  - **Scanned Documents**: Scanned and document files
- **Text**: TXT, Markdown (.md), RTF, LOG, CSV, TEX, JSON, XML, YAML/YML, INI, CFG, CONF, TOML, AsciiDoc (.adoc/.asciidoc), reStructuredText (.rst), PROPERTIES
  - **Markdown**: Markdown and documentation files
  - **Logs**: Log files, error logs, and debug files
  - **Data**: CSV, JSON, XML, YAML data files
  - **Config**: Configuration files (INI, CFG, CONF, TOML, PROPERTIES)
  - **Notes**: Note files, TODO lists, and README files

### Development & Code
- **Code**: Python (.py), JavaScript/TypeScript (.js/.ts/.jsx/.tsx), Shell (.sh), Ruby (.rb), Perl (.pl), C/C++ (.c/.cpp/.h), C# (.cs), Java (.java), Go (.go), Rust (.rs), PHP (.php), Swift (.swift), Kotlin (.kt), Scala (.scala), Dart (.dart), R (.r), Objective-C (.m), Lua (.lua), HTML (.html/.htm), CSS/SCSS/LESS (.css/.scss/.less), Vue (.vue), Svelte (.svelte), SQL (.sql), PowerShell (.ps1)
  - **Python**: Python scripts and modules
  - **JavaScript**: JavaScript, TypeScript, and Node.js files
  - **Web**: HTML, CSS, and web framework files
  - **Scripts**: Shell scripts, batch files, and automation scripts
  - **Mobile**: Swift, Kotlin, and Dart mobile development files
  - **Data Science**: R, MATLAB, and Jupyter notebook files

### Archives & System Files
- **Archives**: ZIP, RAR, 7Z, TAR, TGZ, TAR.GZ, TAR.BZ2, TAR.XZ, GZ, BZ2, XZ, ZST/ZSTD, LZ, LZMA, CAB, ACE, ARJ
  - **Compressed**: ZIP, RAR, 7Z, CAB, ACE, ARJ files
  - **Tarballs**: TAR and compressed TAR files
  - **Backups**: Backup files and archives
  - **Downloads**: Downloaded archive files
- **NonMac**: Windows executables (EXE, MSI, DLL, COM, BAT, CMD, SYS, SCR), Linux packages (RPM, PKG), AppImage
- **DiskImages**: DMG, ISO, IMG, BIN, TOAST, VHD/VHDX, VMDK, QCOW2

### Creative & Professional
- **3DModels**: STL, OBJ, FBX, DAE, 3DS, PLY, GLB, GLTF, BLEND, 3MF, IGS/IGES, STP/STEP
  - **Print Ready**: STL and 3MF files for 3D printing
  - **CAD Models**: IGS, IGES, STP, STEP engineering files
  - **Game Assets**: FBX, GLB, GLTF files for game development
  - **Blender Files**: BLEND files for Blender projects
  - **Scanned Models**: 3D scanned model files
- **MusicScores**: MuseScore (.mscz/.mscx), Guitar Pro (.gp/.gp3/.gp4/.gp5/.gpx/.gp7), MusicXML (.musicxml/.mxl)

### Communication & Organization
- **Emails**: EML, MSG, EMLX, OFT
- **Calendars**: ICS, ICAL, IFB, VCS

### Gaming & Entertainment
- **GameFiles**: Game saves, configurations, and specialized game files
  - **Osu**: osu! game files (.osr, .osz, .osk, .osu)
  - **Minecraft**: JAR, SCHEM/SCHEMATIC, LITEMATIC, LITEMATICA, NBT, MCFUNCTION

### Other Specialized Categories
- **eBooks**: EPUB, MOBI, AZW, AZW3, FB2
- **Fonts**: TTF, OTF, WOFF, WOFF2, FNT
- **Contact files**: VCF, VCARD
- **Databases**: DB, SQLITE, SQL, MDB, ACCDB, ODB, DBF
- **Certificates**: PEM, CER, CRT, PFX, P12, DER, CSR, KEY, P7B, P7C
- **GIS**: SHP, KML, KMZ, GPX, GEOJSON, GML, TIF/TIFF, IMG, ASC
- **Torrents**: TORRENT
- **Sideloading**: IPA, DYLIB, XAPK, mobile provisioning files
- **Subtitles**: SRT, SUB, IDX, SUBRIP, YTP, AEGISUB, SSA, ASS, VTT, TTML
- **Extensionless**: Files without file extensions

## Configuration

### Interactive Configuration Wizard

The easiest way to customize AutoSort is through the interactive configuration wizard:

1. Run `python3 autosort.py`
2. Select "Configuration wizard" from the main menu
3. Choose from the following options:
   - **View current categories**: See all categories with file counts and configuration status
   - **Add new category**: Create custom categories with specific extensions
   - **Edit existing category**: Modify folder names and extensions
   - **Manual update from defaults**: Merge new default categories/extensions with your customizations
   - **Reset to defaults**: Restore default configuration (re-enables auto-updates)
   - **Back to main menu**: Return to the main menu

### Custom Categories with autosort_config.json

The script uses a JSON configuration file (`autosort_config.json`) that allows you to customize categories, file extensions, and folder names without modifying the script.

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
  "metadata": {
    "version": "2.2",
    "auto_generated": false,
    "last_updated": "2025-08-31",
    "note": "This is a custom configuration example - auto-updates are now manual only"
  },
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

See `example_custom_config.json` for a complete example with all available categories.

#### Adding New Categories

1. Use the **Configuration Wizard** (recommended)
2. Or manually edit `autosort_config.json` in a text editor
3. Add a new category object with your desired extensions and folder name
4. Save the file and run the script

#### Image Subfolder Configuration

The Images category supports automatic subfolder organization. You can customize the subcategories by modifying the `subcategories` section:

```json
"Images": {
  "extensions": [".jpg", ".png", ".gif"],
  "folder_name": "Images",
  "subcategories": {
    "Screenshots": {
      "patterns": ["Screenshot*", "Screen Shot*"],
      "exif_indicators": ["no_camera_data"],
      "folder_name": "Screenshots"
    },
    "Adobe_Edited": {
      "exif_indicators": ["Adobe Photoshop", "Adobe Lightroom"],
      "folder_name": "Adobe Edited"
    }
  }
}
```

**Subcategory Properties:**
- `patterns`: Filename patterns to match (supports wildcards)
- `exif_indicators`: EXIF metadata indicators for categorization
- `extensions`: File extensions specific to this subcategory
- `folder_name`: The name of the subfolder

#### Modifying Existing Categories

You can:
- Add new file extensions to existing categories
- Remove file extensions from categories
- Change folder names for categories
- Reorder categories (order doesn't matter)

#### Default Configuration

If no `autosort_config.json` file exists, the script will create one with **29+ default categories** including all the categories listed above. The default configuration is comprehensive and covers most common file types.

#### Smart Configuration Management

The configuration system now uses intelligent management to preserve user customizations:

**User-Modified Configurations:**
- When you make changes via the configuration wizard, `auto_generated` is automatically set to `false`
- This prevents automatic updates from overwriting your customizations
- Your changes are preserved and tracked with timestamps

**Manual Updates:**
- Use "Manual update from defaults" to merge new default categories/extensions with your customizations
- Conflicts are resolved by keeping your customizations
- The configuration remains user-modified after manual updates

**Reset to Defaults:**
- Resetting to defaults sets `auto_generated` back to `true`
- This re-enables automatic updates for the default configuration

**Configuration Status:**
- The wizard shows whether your configuration is auto-generated or user-modified
- User-modified configurations show when they were last changed
- Clear guidance on how to get updates while preserving customizations

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

1. **Startup Menu**: The script prompts you to choose between Desktop organization, custom folder selection, preview mode, or configuration wizard
2. **Preview Mode**: Shows exactly what files will be moved where without actually moving them
3. **Folder Selection**: If you choose custom folder, a native macOS folder picker dialog opens to let you pick any directory
4. **Configuration Loading**: Loads the configuration from `autosort_config.json` (creates default if not exists)
5. **File Analysis**: Analyzes files and shows statistics by category and size
6. **Directory Creation**: Creates an `Autosort` folder in the selected directory
7. **File Scanning**: Scans all files in the selected directory (excluding those in `.sortignore`)
8. **Categorization**: Categorizes each file based on its extension using the configuration
9. **Image Analysis**: For images, analyzes metadata and filename patterns for subfolder categorization
10. **File Moving**: Moves files to appropriate subfolders within `Autosort` (with image subfolders when applicable)
11. **Progress Tracking**: Shows real-time progress with percentage completion
12. **Conflict Resolution**: Handles naming conflicts by appending numbers or timestamps
13. **Error Reporting**: Provides detailed error summaries and troubleshooting information

### Image Subfolder Organization

Images are automatically organized into subfolders based on their characteristics:

- **Screenshots**: Detected by filename patterns (Screenshot*, Screen Shot*) and screenshot software metadata
- **Adobe Edited**: Images processed through Adobe software (Photoshop, Lightroom, Camera Raw)
- **Camera Photos**: Photos with camera EXIF metadata
- **Web Downloads**: Images with common web download naming patterns
- **Design Files**: Professional design formats (PSD, AI, EPS, Sketch, Figma)
- **RAW Photos**: Unprocessed camera RAW formats
- **General**: Other images that don't match specific criteria

## Safety Features

- **Preview Mode**: See what will happen before moving any files
- **Undo System**: Complete undo functionality with persistent history
- **No Overwriting**: Files with duplicate names get unique names
- **Permission Checks**: Verifies read/write permissions before moving files
- **Error Handling**: Graceful handling of permission errors and file access issues
- **Detailed Logging**: Complete record of all operations and errors
- **Progress Tracking**: Real-time feedback on operation progress

## Requirements

- Python 3.8+ (with standard library modules)
- macOS (for Desktop path detection and folder selection dialog)
- Read/write permissions on the directory you want to organize
- tkinter (for GUI version - usually included with Python)

### Dependencies

The script uses Python standard library modules plus one external dependency:
- **Standard Library**: `fnmatch`, `shutil`, `os`, `sys`, `json`, `pathlib`, `typing`, `subprocess`, `time`, `datetime`, `itertools`, `re`, `tkinter` (GUI)
- **External**: `Pillow` (for image metadata analysis)

The script automatically checks for all required dependencies on startup and will display helpful error messages if any are missing. If Pillow is not available, image subfolder categorization will be disabled but the script will continue to function normally.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the script.

