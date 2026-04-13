"""Rich console output helpers for AutoSort."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, List

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.text import Text

console = Console()


def print_welcome(version: str, config_status: Dict[str, Any], undo_info: Dict[str, Any]) -> None:
    grid = Table.grid(padding=(0, 2))
    grid.add_column()
    grid.add_column()
    grid.add_row("Config", f"v{config_status['version']}  ({config_status['status']})")
    grid.add_row("Categories", str(config_status["categories_count"]))
    if undo_info["can_undo"]:
        grid.add_row("Undo", undo_info["last_transaction"])
    console.print(Panel(grid, title=f"[bold]AutoSort[/bold] {version}", border_style="blue"))


def print_results(result, dry_run: bool = False) -> None:
    if result.files_processed == 0:
        console.print("[dim]No files to organize.[/dim]")
        return

    category_counts: Dict[str, int] = {}
    category_sizes: Dict[str, int] = {}
    total_size = 0

    for op in result.operations:
        if op.destination:
            cat = op.destination.parent.name
            category_counts[cat] = category_counts.get(cat, 0) + 1
            try:
                sz = op.source.stat().st_size if op.source.exists() else 0
            except OSError:
                sz = 0
            category_sizes[cat] = category_sizes.get(cat, 0) + sz
            total_size += sz

    table = Table(title="Preview" if dry_run else "Results", show_lines=False)
    table.add_column("Category", style="cyan")
    table.add_column("Files", justify="right", style="green")
    table.add_column("Size", justify="right", style="yellow")

    for cat in sorted(category_counts, key=lambda c: -category_counts[c]):
        table.add_row(cat, str(category_counts[cat]), _fmt_size(category_sizes.get(cat, 0)))

    table.add_section()
    label = "Would move" if dry_run else "Moved"
    table.add_row(
        f"[bold]{label}[/bold]",
        f"[bold]{result.files_processed}[/bold]",
        f"[bold]{_fmt_size(total_size)}[/bold]",
    )
    console.print(table)

    if result.errors > 0:
        console.print(f"\n[red]{result.errors} error(s):[/red]")
        for err in result.error_log[:5]:
            console.print(f"  [dim]{err}[/dim]")
        if len(result.error_log) > 5:
            console.print(f"  [dim]...and {len(result.error_log) - 5} more[/dim]")


def print_file_list(operations, target_root) -> None:
    for op in operations:
        if op.destination:
            try:
                rel = op.destination.relative_to(target_root)
                console.print(f"  [dim]{op.source.name}[/dim] -> [cyan]{rel.parent}/[/cyan]")
            except ValueError:
                console.print(f"  [dim]{op.source.name}[/dim] -> [cyan]{op.destination.parent}/[/cyan]")


def print_undo_history(history: List[Dict[str, Any]]) -> None:
    if not history:
        console.print("[dim]No undo history.[/dim]")
        return
    table = Table(title="Undo History")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Date", style="cyan")
    table.add_column("Description")
    table.add_column("Files", justify="right", style="green")
    for i, tx in enumerate(reversed(history), 1):
        table.add_row(str(i), tx["date"], tx["description"], str(tx["operation_count"]))
    console.print(table)


def print_categories(config: Dict[str, Any]) -> None:
    cats = config.get("categories", {})
    table = Table(title="Categories")
    table.add_column("Category", style="cyan")
    table.add_column("Folder", style="green")
    table.add_column("Extensions", style="dim")
    table.add_column("Subs", justify="right")
    for name, data in sorted(cats.items()):
        exts = data.get("extensions", [])
        ext_str = ", ".join(exts[:5])
        if len(exts) > 5:
            ext_str += f" (+{len(exts) - 5})"
        subs = len(data.get("subcategories", {}))
        table.add_row(name, data.get("folder_name", name), ext_str, str(subs) if subs else "")
    console.print(table)


@contextmanager
def progress_bar():
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        yield progress


def print_success(msg: str) -> None:
    console.print(f"[green]{msg}[/green]")


def print_error(msg: str) -> None:
    console.print(f"[red]{msg}[/red]")


def print_info(msg: str) -> None:
    console.print(f"[blue]{msg}[/blue]")


def _fmt_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    s = float(size_bytes)
    while s >= 1024 and i < len(units) - 1:
        s /= 1024.0
        i += 1
    return f"{s:.1f} {units[i]}"
