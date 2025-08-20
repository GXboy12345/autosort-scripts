# AutoSort - File Organizer

A Python script that automatically organizes files into categorized folders. Can organize your Desktop or any custom folder you select.

**Current Version**: 1.14 (December 2024)

## What's New in v1.14 - Major EUX Improvements

- **🎯 Dry Run Mode**: Preview what files will be moved before actually moving them
- **🔧 Interactive Configuration Wizard**: Easy-to-use menu for customizing categories and settings
- **🖥️ Graphical User Interface**: New GUI version for users who prefer visual interfaces
- **📊 File Analysis & Statistics**: See detailed breakdown of files by category and size
- **📈 Progress Indicators**: Real-time progress tracking with percentage completion
- **🎨 Enhanced Visual Feedback**: Emojis and color-coded status messages
- **⚠️ Better Error Reporting**: Detailed error summaries and troubleshooting information
- **🔄 Improved User Flow**: Streamlined menus and clearer navigation
- **🔒 Smart Configuration Management**: Manual updates with conflict resolution, auto-updates disabled for user modifications

## What's New in v1.13

- **Smart Image Subfolder Organization**: Automatically categorizes images into subfolders based on metadata and filename patterns
- **Screenshot Detection**: Identifies and separates screenshots from other images using filename patterns and EXIF data
- **Adobe Software Detection**: Recognizes images processed through Adobe Photoshop, Lightroom, and Camera Raw
- **Camera Photo Identification**: Separates camera photos based on EXIF metadata
- **Design File Organization**: Groups design files (PSD, AI, EPS) separately from regular images
- **RAW Photo Support**: Dedicated subfolder for RAW camera formats

## Features

- **Flexible Source Selection**: Choose between organizing your Desktop or any custom folder
- **Preview Mode**: See what will happen before moving any files (dry run)
- **Interactive Configuration**: Easy-to-use wizard for customizing categories and settings
- **Graphical Interface**: Both command-line and GUI versions available
- **Automatic Categorization**: Files are sorted into categories based on their file extensions
- **Configurable Categories**: Customize categories, file types, and folder names via JSON configuration
- **Cross-platform Desktop Detection**: Works with different locale Desktop folder names (Desktop, Escritorio, Bureau, etc.)
- **Safe File Handling**: Prevents overwriting files and handles naming conflicts
- **Ignore Patterns**: Support for `.sortignore` file to exclude specific files
- **Comprehensive File Types**: Supports images, audio, video, documents, code, archives, and more
- **Progress Tracking**: Real-time progress indicators and detailed statistics
- **Smart Image Organization**: Advanced image categorization with subfolders

## Installation

1. Clone or download this repository
2. Ensure you have Python 3.6+ installed
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
3. **Organize custom folder** - Choose any folder to organize using a folder selection dialog
4. **Preview Desktop organization (dry run)** - See what would happen without moving files
5. **Preview Downloads organization (dry run)** - See what would happen without moving files
6. **Preview custom folder organization (dry run)** - See what would happen without moving files
7. **Configuration wizard** - Customize categories and settings
8. **Exit** - Quit the script

### Graphical User Interface
```bash
python3 autosort_gui.py
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

### macOS Double-Click
- **Command Line**: Double-click `run-autosort.command`
- **GUI**: Double-click `run-autosort-gui.command`

## EUX Improvements

### 🎯 Dry Run Mode
The new preview mode lets you see exactly what files will be moved where before actually moving them:

```
📋 Preview Summary: 15 files would be organized
💡 Run the script again and choose option 1 or 2 to actually move the files
```

This eliminates anxiety about losing files and helps users understand the organization process.

### 🔧 Configuration Wizard
The interactive configuration wizard makes it easy to customize AutoSort:

- **View current categories** with file counts and sizes
- **Add new categories** with custom extensions
- **Edit existing categories** (rename folders, add/remove extensions)
- **Toggle auto-updates** for configuration changes
- **Reset to defaults** if needed

### 📊 File Analysis & Statistics
Before organizing, AutoSort shows detailed statistics:

```
📊 File Analysis
------------------------------
📁 Total files: 47
💾 Total size: 2.3 GB

📋 Files by category:
  Images: 23 files (1.8 GB)
  Documents: 12 files (156.2 MB)
  Audio: 8 files (245.7 MB)
  Video: 4 files (89.1 MB)
```

### 📈 Progress Tracking
Real-time progress indicators show exactly what's happening:

```
📊 Progress: 45.2% (21/47)
📄 Would move 'document.pdf' → 'Documents/'
```

### 🎨 Enhanced Visual Feedback
Color-coded status messages and emojis make it easy to understand what's happening:

- ✅ Success messages
- ❌ Error messages  
- ⚠️ Warning messages
- 📋 Information messages
- 🔄 Progress updates

### ⚠️ Better Error Reporting
Detailed error summaries help users troubleshoot issues:

```
⚠️ Error Summary
--------------------

PermissionError (3 occurrences):
  • Failed to move important.pdf
  • Failed to move project.zip
  • Failed to move backup.db
```

## Supported File Categories

The script supports **25+ categories** with comprehensive file type coverage:

### Core Media Categories
- **Images**: JPG, JPEG 2000 (JP2, J2K, JPF, JPX), PNG, GIF, BMP, TIFF/TIF, HEIC, RAW formats (CR2, NEF, ARW, ORF, DNG), SVG, WebP, AVIF, JXL, PSD, AI, EPS, ICO, ICNS, TGA
  - **Screenshots**: Automatically detected screenshots (macOS, Windows patterns)
  - **Adobe Edited**: Images processed through Adobe software (Photoshop, Lightroom, Camera Raw)
  - **Camera Photos**: Photos taken with digital cameras (identified via EXIF metadata)
  - **Web Downloads**: Images downloaded from the web (common naming patterns)
  - **Design Files**: Professional design files (PSD, AI, EPS, Sketch, Figma)
  - **RAW Photos**: Unprocessed camera RAW files
  - **General**: Other images that don't fit specific categories
- **Audio**: MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, AMR, WMA, AIFF, ALAC, MIDI/MID, WV, RA, APE, DTS
- **Video**: MP4, MOV, AVI, MKV, FLV, WMV, WebM, M4V, 3GP, MPEG/MPG, TS, M2TS, MTS, DIVX, OGV, VOB, RM, ASF, MXF, H264, HEVC/H265

### Document Categories
- **Documents**: PDF, DOC/DOCX, Pages, ODT
- **Spreadsheets**: XLS/XLSX/XLSM, CSV, TSV
- **Presentations**: PPT/PPTX, PPS/PPSX
- **Text**: TXT, Markdown (.md), RTF, LOG, CSV, TEX, JSON, XML, YAML/YML, INI, CFG, CONF, TOML, AsciiDoc (.adoc/.asciidoc), reStructuredText (.rst), PROPERTIES

### Development & Code
- **Code**: Python (.py), JavaScript/TypeScript (.js/.ts/.jsx/.tsx), Shell (.sh), Ruby (.rb), Perl (.pl), C/C++ (.c/.cpp/.h), C# (.cs), Java (.java), Go (.go), Rust (.rs), PHP (.php), Swift (.swift), Kotlin (.kt), Scala (.scala), Dart (.dart), R (.r), Objective-C (.m), Lua (.lua), HTML (.html/.htm), CSS/SCSS/LESS (.css/.scss/.less), Vue (.vue), Svelte (.svelte), SQL (.sql), PowerShell (.ps1)

### Archives & System Files
- **Archives**: ZIP, RAR, 7Z, TAR, TGZ, TAR.GZ, TAR.BZ2, TAR.XZ, GZ, BZ2, XZ, ZST/ZSTD, LZ, LZMA, CAB, ACE, ARJ
- **NonMac**: Windows executables (EXE, MSI, DLL, COM, BAT, CMD, SYS, SCR), Linux packages (RPM, PKG), AppImage
- **DiskImages**: DMG, ISO, IMG, BIN, TOAST, VHD/VHDX, VMDK, QCOW2

### Creative & Professional
- **3DModels**: STL, OBJ, FBX, DAE, 3DS, PLY, GLB, GLTF, BLEND, 3MF, IGS/IGES, STP/STEP
- **VideoProjects**: Adobe Premiere (.prproj), Vegas (.veg), DaVinci Resolve (.drp), Final Cut Pro (.fcpxml), After Effects (.aep)
- **AudioProjects**: FL Studio (.flp), Ableton Live (.als), Audacity (.aup/.aup3), Pro Tools (.sesx/.ptx), Reaper (.rpp/.rpl/.rpreset)
- **MusicScores**: MuseScore (.mscz/.mscx)

### Specialized Categories
- **Minecraft**: JAR, SCHEM/SCHEMATIC, LITEMATIC, NBT, MCFUNCTION
- **eBooks**: EPUB, MOBI, AZW, AZW3, FB2
- **Fonts**: TTF, OTF, WOFF, WOFF2, FNT
- **Contact files**: VCF, VCARD
- **Databases**: DB, SQLITE, SQL, MDB, ACCDB, ODB, DBF
- **Certificates**: PEM, CER, CRT, PFX, P12, DER, CSR, KEY, P7B, P7C
- **GIS**: SHP, KML, KMZ, GPX, GEOJSON, GML, TIF/TIFF, IMG, ASC
- **Torrents**: TORRENT
- **Sideloading**: IPA, DYLIB, XAPK, mobile provisioning files
- **Subtitles**: SRT, SUB, IDX, SUBRIP, YTP, AEGISUB, SSA, ASS, VTT, TTML

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
    "version": "1.14",
    "auto_generated": false,
    "last_updated": "2024-12-01",
    "note": "This is a custom configuration example"
  },
  "categories": {
    "MyCustomCategory": {
      "extensions": [".myfile", ".custom", ".special"],
      "folder_name": "My Custom Files"
    },
    "Images": {
      "extensions": [".jpg", ".png", ".gif"],
      "folder_name": "Images"
    },
    "VideoProjects": {
      "extensions": [".prproj", ".veg", ".drp"],
      "folder_name": "Video Projects"
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

If no `autosort_config.json` file exists, the script will create one with **25+ default categories** including all the categories listed above. The default configuration is comprehensive and covers most common file types.

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
- **Version checking**: Automatically checks for updates from the remote configuration before showing the menu
- **Update notifications**: Alerts users when newer configuration versions are available
- **Smart version handling**: Handles unusual cases where local version might be newer than remote

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
- **No Overwriting**: Files with duplicate names get unique names
- **Permission Checks**: Verifies read/write permissions before moving files
- **Error Handling**: Graceful handling of permission errors and file access issues
- **Detailed Logging**: Complete record of all operations and errors
- **Progress Tracking**: Real-time feedback on operation progress

## Requirements

- Python 3.6+ (with standard library modules)
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

The MIT License is a permissive license that allows others to use, modify, and distribute your code with very few restrictions. It's one of the most popular open source licenses due to its simplicity and permissiveness.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the script. 