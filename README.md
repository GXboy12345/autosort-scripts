# AutoSort - File Organizer

A Python script that automatically organizes files into categorized folders. Can organize your Desktop or any custom folder you select.

**Current Version**: 1.13 (August 2025)

## What's New in v1.13

- **Smart Image Subfolder Organization**: Automatically categorizes images into subfolders based on metadata and filename patterns
- **Screenshot Detection**: Identifies and separates screenshots from other images using filename patterns and EXIF data
- **Adobe Software Detection**: Recognizes images processed through Adobe Photoshop, Lightroom, and Camera Raw
- **Camera Photo Identification**: Separates camera photos based on EXIF metadata
- **Design File Organization**: Groups design files (PSD, AI, EPS) separately from regular images
- **RAW Photo Support**: Dedicated subfolder for RAW camera formats

## What's New in v1.12

- **Consolidated Audio Projects**: Merged Reaper files into the AudioProjects category for better organization
- **Enhanced Audio Project Support**: Comprehensive coverage for FL Studio, Ableton Live, Audacity, Pro Tools, and Reaper

## What's New in v1.11

- **Flexible Source Selection**: Choose between Desktop or any custom folder via native folder picker
- **25+ Comprehensive Categories**: Added specialized categories for creative professionals, developers, and power users
- **Enhanced File Type Support**: Extended coverage for video projects, audio projects, 3D models, GIS data, and more
- **Improved Organization**: Separated documents into specific categories (Spreadsheets, Presentations, etc.)
- **Better Configuration Management**: Enhanced auto-update system with version tracking

## Features

- **Flexible Source Selection**: Choose between organizing your Desktop or any custom folder
- **Automatic Categorization**: Files are sorted into categories based on their file extensions
- **Configurable Categories**: Customize categories, file types, and folder names via JSON configuration
- **Cross-platform Desktop Detection**: Works with different locale Desktop folder names (Desktop, Escritorio, Bureau, etc.)
- **Safe File Handling**: Prevents overwriting files and handles naming conflicts
- **Ignore Patterns**: Support for `.sortignore` file to exclude specific files
- **Comprehensive File Types**: Supports images, audio, video, documents, code, archives, and more

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

### Command Line
```bash
python3 autosort.py
```

The script will prompt you to choose:
1. **Organize Desktop** - Sort files from your Desktop folder
2. **Select custom folder** - Choose any folder to organize using a folder selection dialog
3. **Exit** - Quit the script

### Folder Selection
When you choose "Select custom folder", a native macOS folder picker dialog will open, allowing you to:
- Navigate to any directory on your system
- Select the folder you want to organize
- The script will create an `Autosort` folder within your selected directory

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
  "metadata": {
    "version": "1.13",
    "auto_generated": false,
    "last_updated": "2025-08-09",
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

1. Open `autosort_config.json` in a text editor
2. Add a new category object with your desired extensions and folder name
3. Save the file and run the script

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

1. **Startup Menu**: The script prompts you to choose between Desktop organization or custom folder selection
2. **Folder Selection**: If you choose custom folder, a native macOS folder picker dialog opens to let you pick any directory
3. **Configuration Loading**: Loads the configuration from `autosort_config.json` (creates default if not exists)
4. **Directory Creation**: Creates an `Autosort` folder in the selected directory
5. **File Scanning**: Scans all files in the selected directory (excluding those in `.sortignore`)
6. **Categorization**: Categorizes each file based on its extension using the configuration
7. **Image Analysis**: For images, analyzes metadata and filename patterns for subfolder categorization
8. **File Moving**: Moves files to appropriate subfolders within `Autosort` (with image subfolders when applicable)
9. **Conflict Resolution**: Handles naming conflicts by appending numbers or timestamps

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

- **No Overwriting**: Files with duplicate names get unique names
- **Permission Checks**: Verifies read/write permissions before moving files
- **Error Handling**: Graceful handling of permission errors and file access issues
- **Dry Run**: Consider testing on a small set of files first

## Requirements

- Python 3.6+ (with standard library modules)
- macOS (for Desktop path detection and folder selection dialog)
- Read/write permissions on the directory you want to organize

### Dependencies

The script uses Python standard library modules plus one external dependency:
- **Standard Library**: `fnmatch`, `shutil`, `os`, `sys`, `json`, `pathlib`, `typing`, `subprocess`, `time`, `datetime`, `itertools`, `re`
- **External**: `Pillow` (for image metadata analysis)

The script automatically checks for all required dependencies on startup and will display helpful error messages if any are missing. If Pillow is not available, image subfolder categorization will be disabled but the script will continue to function normally.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that allows others to use, modify, and distribute your code with very few restrictions. It's one of the most popular open source licenses due to its simplicity and permissiveness.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the script. 