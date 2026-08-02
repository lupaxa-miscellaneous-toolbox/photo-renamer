"""Rich progress bar helpers."""

from __future__ import annotations

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn


def make_progress(console: Console, total: int, description: str) -> Progress:
    """Return a determinate Rich progress bar bound to *console*."""
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
        console=console,
    )
    progress.add_task(description, total=total)
    return progress
