# AutoSort

Automatic file organizer for macOS. Sorts files into categorized folders based on type,
with real-time watching, undo support, and an interactive terminal UI.

## Install

```bash
pipx install .
# or
pip install .
```

## Quick Start

```bash
autosort run ~/Desktop              # sort files on your Desktop
autosort run ~/Downloads --dry-run  # preview without moving anything
autosort watch                      # auto-sort new files in real time
autosort undo                       # reverse the last operation
autosort                            # open the interactive TUI
```

## Commands

| Command | Description |
|---------|-------------|
| `autosort` | Launch interactive terminal UI |
| `autosort run [PATH]` | One-shot sort (supports `--desktop`, `--downloads`, `--dry-run`) |
| `autosort watch [PATHS...]` | Watch directories and auto-sort new files (`--desktop`, `--downloads`) |
| `autosort undo` | Undo the last sort operation (`--list` for history) |
| `autosort config show` | Display current category configuration |
| `autosort config edit` | Open config in `$EDITOR` |
| `autosort config reset` | Reset to default categories |
| `autosort config path` | Print config file location |
| `autosort install` | Install a LaunchAgent to auto-sort on login |
| `autosort uninstall` | Remove the LaunchAgent |

## How It Works

1. Scans the target directory for files (non-recursive)
2. Categorizes each file by extension, with optional subcategories via filename patterns and EXIF metadata
3. Moves files into an `Autosort/` subfolder organized by category
4. Records every operation for undo

Files matching patterns in `.sortignore` (placed in the target directory or `~/.config/autosort/`) are skipped.

## Categories

AutoSort ships with 30+ categories covering common file types:

- **Media** -- Images (with Screenshots, RAW, Adobe Edited subcategories), Audio, Video
- **Documents** -- PDFs, Word, Pages, Spreadsheets, Presentations
- **Code** -- Python, JavaScript, Web, Scripts, Mobile, Data Science
- **Archives** -- Compressed, Tarballs, Backups
- **Creative** -- 3D Models, Music Scores, Video/Audio Projects, Fonts
- **System** -- Disk Images, Non-Mac Files, Certificates, Databases
- **Other** -- eBooks, Emails, Calendars, Game Files, Torrents, Subtitles, and more

All categories are fully customizable via `~/.config/autosort/config.json`.

## Configuration

Configuration lives at `~/.config/autosort/config.json` and is created automatically on first run.

```bash
autosort config show    # view all categories
autosort config edit    # open in your editor
autosort config reset   # restore defaults
```

Each category defines a list of extensions and a folder name. Categories can include subcategories
with filename patterns and EXIF indicators for finer-grained sorting.

## Watch Mode

```bash
autosort watch                      # watch Desktop + Downloads
autosort watch ~/Desktop --quiet    # watch one directory, suppress notifications
autosort install --desktop          # auto-start on login via LaunchAgent
```

Watch mode uses macOS FSEvents for efficient file system monitoring with debounced batching.
A macOS notification is sent when files are sorted.

## Undo

Every sort operation is recorded as a transaction. Undo moves files back to their original locations.

```bash
autosort undo           # undo the last operation
autosort undo --list    # show full undo history
```

History is persisted at `~/.config/autosort/undo.json` and retains the last 50 transactions.

## Requirements

- macOS
- Python 3.10+

## License

MIT License. See [LICENSE](LICENSE) for details.
