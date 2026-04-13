"""Textual TUI application for AutoSort."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Footer, Header, Label, RichLog, Static

from autosort import __version__
from autosort.core.config import ConfigManager
from autosort.core.organizer import FileOrganizer, OrganizationResult
from autosort.core.paths import PathManager
from autosort.services.undo import UndoManager


class AutoSortApp(App):
    """Interactive terminal UI for AutoSort."""

    CSS_PATH = "app.tcss"
    TITLE = "AutoSort"
    SUB_TITLE = f"v{__version__}"

    BINDINGS = [
        Binding("d", "sort_desktop", "Sort Desktop"),
        Binding("l", "sort_downloads", "Sort Downloads"),
        Binding("b", "browse", "Browse"),
        Binding("w", "watch_toggle", "Watch"),
        Binding("u", "undo_last", "Undo"),
        Binding("c", "show_config", "Config"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.cm = ConfigManager()
        self.cm.load_config()
        self.pm = PathManager()
        self.um = UndoManager()
        self.fo = FileOrganizer(self.cm, self.pm, self.um)
        self._watching = False
        self._watcher = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main-container"):
            with Horizontal(classes="action-bar"):
                yield Button("Sort Desktop", id="btn-desktop", variant="primary")
                yield Button("Sort Downloads", id="btn-downloads", variant="primary")
                yield Button("Browse...", id="btn-browse")
                yield Button("Watch", id="btn-watch", variant="success")
                yield Button("Undo", id="btn-undo", variant="warning")
                yield Button("Config", id="btn-config")
            yield RichLog(id="log-panel", highlight=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#log-panel", RichLog)
        info = self.cm.get_status_info()
        undo = self.um.get_undo_info()
        log.write(f"[bold blue]AutoSort v{__version__}[/bold blue]")
        log.write(f"Config v{info['version']} | {info['categories_count']} categories")
        if undo["can_undo"]:
            log.write(f"Undo available: {undo['last_transaction']}")
        log.write("")
        log.write("[dim]Press 'd' for Desktop, 'l' for Downloads, 'b' to browse, 'w' to watch[/dim]")

    @on(Button.Pressed, "#btn-desktop")
    def on_desktop(self) -> None:
        self.action_sort_desktop()

    @on(Button.Pressed, "#btn-downloads")
    def on_downloads(self) -> None:
        self.action_sort_downloads()

    @on(Button.Pressed, "#btn-browse")
    def on_browse(self) -> None:
        self.action_browse()

    @on(Button.Pressed, "#btn-watch")
    def on_watch(self) -> None:
        self.action_watch_toggle()

    @on(Button.Pressed, "#btn-undo")
    def on_undo(self) -> None:
        self.action_undo_last()

    @on(Button.Pressed, "#btn-config")
    def on_config(self) -> None:
        self.action_show_config()

    def action_sort_desktop(self) -> None:
        self._run_sort(self.pm.get_desktop_path())

    def action_sort_downloads(self) -> None:
        self._run_sort(self.pm.get_downloads_path())

    def action_browse(self) -> None:
        selected = self.pm.select_folder_dialog()
        if selected:
            self._run_sort(selected)
        else:
            self._log("No folder selected.")

    def action_watch_toggle(self) -> None:
        if self._watching:
            self._stop_watching()
        else:
            self._start_watching()

    def action_undo_last(self) -> None:
        info = self.um.get_undo_info()
        if not info["can_undo"]:
            self._log("[yellow]Nothing to undo.[/yellow]")
            return
        self._log(f"Undoing: {info['last_transaction']}...")
        if self.um.undo_last_transaction():
            self._log("[green]Undo complete.[/green]")
        else:
            self._log("[red]Undo failed.[/red]")

    def action_show_config(self) -> None:
        log = self.query_one("#log-panel", RichLog)
        log.write("")
        cats = self.cm.get_config().get("categories", {})
        log.write(f"[bold]{len(cats)} categories:[/bold]")
        for name, data in sorted(cats.items()):
            exts = data.get("extensions", [])
            ext_str = ", ".join(exts[:4])
            if len(exts) > 4:
                ext_str += f" (+{len(exts) - 4})"
            rules = data.get("rules") or []
            nrules = len(rules) if isinstance(rules, list) else 0
            sub_str = f" [{nrules} rules]" if nrules else ""
            log.write(f"  [cyan]{data.get('folder_name', name)}[/cyan]: {ext_str}{sub_str}")
            if isinstance(rules, list) and rules:
                for r in sorted(rules, key=lambda x: -int(x.get("priority", 0)))[:8]:
                    rname = r.get("name", "")
                    pri = r.get("priority", "")
                    folder = r.get("folder", "")
                    log.write(f"      [dim]p{pri}[/dim] [yellow]{rname}[/yellow] -> {folder}")
                if len(rules) > 8:
                    log.write(f"      [dim]... +{len(rules) - 8} more[/dim]")

    @work(thread=True)
    def _run_sort(self, source: Path) -> None:
        log = self.query_one("#log-panel", RichLog)
        log.write(f"\n[bold]Organizing {source.name}...[/bold]")

        ignore = source / ".sortignore"
        if ignore.exists():
            self.fo.load_ignore_patterns(ignore)

        tid = self.um.start_transaction(f"Organize {source.name}")
        self.fo.set_current_transaction(tid)
        self.fo.invalidate_cache()

        def cb(current, total, name):
            self.call_from_thread(
                log.write, f"  [{current}/{total}] {name}"
            )

        self.fo.set_progress_callback(cb)
        result = self.fo.organize_directory(source, dry_run=False)

        if result.files_moved > 0:
            self.um.commit_transaction(tid)
            self.call_from_thread(
                log.write,
                f"[green]Done: {result.files_moved} files sorted, {result.errors} errors[/green]",
            )
            from autosort.console import notify_category_counts
            from autosort.services.notify import notify_sort_complete

            notify_sort_complete(notify_category_counts(result.operations))
        else:
            self.call_from_thread(log.write, "[dim]No files to organize.[/dim]")

    def _start_watching(self) -> None:
        from autosort.core.watcher import DirectoryWatcher

        dirs = [self.pm.get_desktop_path(), self.pm.get_downloads_path()]
        log = self.query_one("#log-panel", RichLog)
        btn = self.query_one("#btn-watch", Button)

        for d in dirs:
            ig = d / ".sortignore"
            if ig.exists():
                self.fo.load_ignore_patterns(ig)

        def on_files(files: list[Path]):
            for fp in files:
                if not fp.exists():
                    continue
                parent = fp.parent
                tid = self.um.start_transaction(f"Auto-sort {fp.name}")
                self.fo.set_current_transaction(tid)
                self.fo.invalidate_cache()
                result = self.fo.organize_directory(parent, dry_run=False)
                if result.files_moved > 0:
                    self.um.commit_transaction(tid)
                    self.call_from_thread(
                        log.write,
                        f"[green]Auto-sorted {result.files_moved} file(s)[/green]",
                    )

        self._watcher = DirectoryWatcher(dirs, on_files, debounce=1.5)
        self._watcher.start()
        self._watching = True
        btn.label = "Stop Watch"
        btn.variant = "error"
        log.write("[green]Watching Desktop & Downloads...[/green]")

    def _stop_watching(self) -> None:
        if self._watcher:
            self._watcher.stop()
            self._watcher = None
        self._watching = False
        btn = self.query_one("#btn-watch", Button)
        btn.label = "Watch"
        btn.variant = "success"
        self._log("[yellow]Watch stopped.[/yellow]")

    def _log(self, msg: str) -> None:
        self.query_one("#log-panel", RichLog).write(msg)


def run_app() -> None:
    app = AutoSortApp()
    app.run()
