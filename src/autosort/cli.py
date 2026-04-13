"""Click CLI entry point for AutoSort."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

from autosort import __version__
from autosort.console import (
    console,
    notify_category_counts,
    print_categories,
    print_error,
    print_file_list,
    print_info,
    print_results,
    print_success,
    print_undo_history,
    print_welcome,
    progress_bar,
)
from autosort.core.config import ConfigManager
from autosort.core.organizer import FileOrganizer
from autosort.core.paths import PathManager
from autosort.services.undo import UndoManager


def _boot():
    cm = ConfigManager()
    cm.load_config()
    pm = PathManager()
    um = UndoManager()
    fo = FileOrganizer(cm, pm, um)
    return cm, pm, um, fo


def _resolve_path(path: str | None, desktop: bool, downloads: bool, pm: PathManager) -> Path | None:
    if desktop:
        return pm.get_desktop_path()
    if downloads:
        return pm.get_downloads_path()
    if path:
        return Path(path).expanduser().resolve()
    return None


class DefaultGroup(click.Group):
    """Falls through to the TUI when no subcommand is given."""

    def parse_args(self, ctx, args):
        if not args or (args[0].startswith("-") and args[0] not in ("--help", "--version")):
            args = ["tui"] + args
        return super().parse_args(ctx, args)


@click.group(cls=DefaultGroup, invoke_without_command=True)
@click.version_option(__version__, prog_name="autosort")
def cli():
    """AutoSort - Automatic file organizer for macOS."""
    pass


@cli.command()
def tui():
    """Launch the interactive terminal UI."""
    from autosort.app import run_app
    run_app()


@cli.command()
@click.argument("path", required=False)
@click.option("--desktop", is_flag=True, help="Organize ~/Desktop")
@click.option("--downloads", is_flag=True, help="Organize ~/Downloads")
@click.option("--dry-run", is_flag=True, help="Preview without moving files")
@click.option("--quiet", is_flag=True, help="Suppress notifications")
def run(path, desktop, downloads, dry_run, quiet):
    """Sort files in a directory."""
    cm, pm, um, fo = _boot()
    target = _resolve_path(path, desktop, downloads, pm)
    if target is None:
        target = pm.select_folder_dialog()
    if target is None:
        print_error("No directory selected.")
        raise SystemExit(1)

    ignore_file = target / ".sortignore"
    if not ignore_file.exists():
        ignore_file = Path.home() / ".config" / "autosort" / ".sortignore"
    fo.load_ignore_patterns(ignore_file)

    tid = None
    if not dry_run:
        tid = um.start_transaction(f"Organize {target.name}")
        fo.set_current_transaction(tid)

    with progress_bar() as prog:
        task = prog.add_task(f"{'Preview' if dry_run else 'Organizing'} {target.name}", total=0)

        def cb(current, total, name):
            prog.update(task, total=total, completed=current, description=name)

        fo.set_progress_callback(cb)
        result = fo.organize_directory(target, dry_run=dry_run)

    console.print()
    print_results(result, dry_run=dry_run)

    if dry_run and result.operations:
        target_root = pm.get_target_path(target)
        print_file_list(result.operations, target_root)

    if not dry_run and tid and result.files_moved > 0:
        um.commit_transaction(tid)
        if not quiet:
            from autosort.services.notify import notify_sort_complete
            notify_sort_complete(notify_category_counts(result.operations), quiet=quiet)

    raise SystemExit(0 if result.success else 1)


@cli.command()
@click.argument("paths", nargs=-1)
@click.option("--desktop", is_flag=True, help="Watch ~/Desktop")
@click.option("--downloads", is_flag=True, help="Watch ~/Downloads")
@click.option("--quiet", is_flag=True, help="Suppress notifications")
def watch(paths, desktop, downloads, quiet):
    """Watch directories and auto-sort new files."""
    from autosort.core.watcher import DirectoryWatcher
    from autosort.services.notify import notify_sort_complete

    cm, pm, um, fo = _boot()

    dirs: list[Path] = []
    if desktop:
        dirs.append(pm.get_desktop_path())
    if downloads:
        dirs.append(pm.get_downloads_path())
    for p in paths:
        dirs.append(Path(p).expanduser().resolve())
    if not dirs:
        dirs = [pm.get_desktop_path(), pm.get_downloads_path()]

    for d in dirs:
        ignore_file = d / ".sortignore"
        if ignore_file.exists():
            fo.load_ignore_patterns(ignore_file)

    def on_files(new_files: list[Path]):
        for fp in new_files:
            if not fp.exists() or not fp.is_file():
                continue
            parent = fp.parent
            target = pm.get_target_path(parent)
            tid = um.start_transaction(f"Auto-sort {fp.name}")
            fo.set_current_transaction(tid)
            fo.invalidate_cache()
            result = fo.organize_directory(parent, dry_run=False)
            if result.files_moved > 0:
                um.commit_transaction(tid)
                notify_sort_complete(notify_category_counts(result.operations), quiet=quiet)
                if not quiet:
                    console.print(f"[green]Sorted {result.files_moved} file(s)[/green]")

    console.print(f"[blue]Watching {len(dirs)} directory(ies)... Press Ctrl+C to stop.[/blue]")
    for d in dirs:
        console.print(f"  [dim]{d}[/dim]")

    watcher = DirectoryWatcher(dirs, on_files, debounce=1.5)
    watcher.run_forever()


@cli.command()
@click.option("--list", "show_list", is_flag=True, help="Show undo history")
def undo(show_list):
    """Undo the last file organization."""
    cm, pm, um, fo = _boot()

    if show_list:
        print_undo_history(um.get_transaction_history())
        return

    info = um.get_undo_info()
    if not info["can_undo"]:
        print_info("Nothing to undo.")
        return

    console.print(f"Undo: [cyan]{info['last_transaction']}[/cyan] ({info['last_file_count']} files)")
    if not click.confirm("Proceed?"):
        return

    if um.undo_last_transaction():
        print_success("Undo complete.")
    else:
        print_error("Undo failed (some files may have been partially restored).")


@cli.group()
def config():
    """View and manage configuration."""
    pass


@config.command()
def show():
    """Display current configuration."""
    cm = ConfigManager()
    cm.load_config()
    print_categories(cm.get_config())


@config.command()
def reset():
    """Reset configuration to defaults."""
    cm = ConfigManager()
    cm.load_config()
    if click.confirm("Reset to default configuration?"):
        cm.reset_to_defaults()
        print_success("Configuration reset to defaults.")


@config.command()
def edit():
    """Open configuration in $EDITOR."""
    import os
    import subprocess
    cm = ConfigManager()
    cm.load_config()
    editor = os.environ.get("EDITOR", "nano")
    subprocess.run([editor, str(cm.config_path)])


@config.command("path")
def config_path():
    """Print configuration file path."""
    cm = ConfigManager()
    click.echo(cm.config_path)


@cli.command()
@click.argument("paths", nargs=-1)
@click.option("--desktop", is_flag=True, help="Watch ~/Desktop")
@click.option("--downloads", is_flag=True, help="Watch ~/Downloads")
def install(paths, desktop, downloads):
    """Install LaunchAgent for auto-sorting on login."""
    from autosort.services import launchd

    pm = PathManager()
    watch_paths: list[str] = []
    if desktop:
        watch_paths.append(str(pm.get_desktop_path()))
    if downloads:
        watch_paths.append(str(pm.get_downloads_path()))
    for p in paths:
        watch_paths.append(str(Path(p).expanduser().resolve()))
    if not watch_paths:
        watch_paths = [str(pm.get_desktop_path()), str(pm.get_downloads_path())]

    plist = launchd.install(watch_paths)
    print_success(f"LaunchAgent installed: {plist}")
    print_info("AutoSort will now start watching on login.")


@cli.command()
def uninstall():
    """Remove the AutoSort LaunchAgent."""
    from autosort.services import launchd

    if launchd.uninstall():
        print_success("LaunchAgent removed.")
    else:
        print_info("No LaunchAgent found.")
