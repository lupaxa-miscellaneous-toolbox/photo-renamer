"""Startup summary, run statistics, and tab-separated log file writer."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import Self, TextIO

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from lupaxa.photo_renamer.config import AppConfig
from lupaxa.photo_renamer.models import RunStats


def print_startup(console: Console, config: AppConfig, file_count: int) -> None:
    """Print a Rich panel summarising the run configuration."""
    if config.quiet:
        return

    operation = "move" if config.move else "copy"
    if config.dry_run:
        operation = f"dry-run ({operation})"

    lines = [
        f"Root: {config.root}",
        f"Output: {config.output_dir}",
        f"Files: {file_count}",
        f"Workers: {config.workers}",
        f"Operation: {operation}",
        f"Recursive: {config.recursive}",
        f"Format: {config.name_format}",
        f"Timestamp: {config.timestamp_mode}",
    ]
    if config.organise:
        lines.append("Organise: yes")
    if config.flatten:
        lines.append("Flatten: yes")

    console.print(Panel("\n".join(lines), title="photo-renamer", expand=False))


def print_summary(console: Console, stats: RunStats) -> None:
    """Print a Rich table with aggregated run counters."""
    table = Table(title="Summary", show_header=True, header_style="bold")
    table.add_column("Metric", style="dim")
    table.add_column("Count", justify="right")
    table.add_row("Scanned", str(stats.scanned))
    table.add_row("Processed", str(stats.processed))
    table.add_row("Skipped", str(stats.skipped))
    table.add_row("Failed", str(stats.failed))
    table.add_row("Collisions", str(stats.collisions))
    table.add_row("Metadata missing", str(stats.metadata_missing))
    console.print(table)


class LogWriter:
    """Append tab-separated rename events to a log file."""

    def __init__(self: Self, path: Path) -> None:
        self._path = path
        self._file: TextIO | None = None

    def __enter__(self: Self) -> Self:
        """Open the log file for append."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self._path.open("a", encoding="utf-8")
        return self

    def __exit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Close the log file."""
        if self._file is not None:
            self._file.close()
            self._file = None

    def write_event(
        self: Self,
        action: str,
        source: Path,
        destination: Path | None,
        source_label: str,
        origin: str,
        message: str = "",
    ) -> None:
        """Write one tab-separated log line for a rename event."""
        if self._file is None:
            msg = "LogWriter is not open"
            raise RuntimeError(msg)

        timestamp = datetime.now(tz=UTC).isoformat(timespec="seconds")
        dest_value = str(destination) if destination is not None else "-"
        line = (
            f"{timestamp}\t{action}\t{source}\t{dest_value}\t{source_label}\t{origin}\t{message}\n"
        )
        self._file.write(line)
        self._file.flush()
