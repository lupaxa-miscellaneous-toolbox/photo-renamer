"""Tests for reporting helpers and log file writer."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from lupaxa.photo_renamer.config import AppConfig
from lupaxa.photo_renamer.reporting import LogWriter, print_startup


def _cfg(root: Path, **kwargs: object) -> AppConfig:
    base = {
        "root": root.resolve(),
        "output_dir": (root / "renamed").resolve(),
        "recursive": False,
        "dry_run": False,
        "verbose": False,
        "quiet": False,
        "force": False,
        "skip_existing": False,
        "timestamp_mode": "filesystem",
        "name_format": "datetime",
        "organise": False,
        "flatten": False,
        "move": False,
        "include": None,
        "exclude": None,
        "timezone": None,
        "log_file": None,
        "workers": 1,
        "assume_yes": False,
    }
    base.update(kwargs)
    return AppConfig(**base)  # type: ignore[arg-type]


def test_print_startup_shows_workers(tmp_path: Path) -> None:
    console = Console(record=True, width=120)
    print_startup(console, _cfg(tmp_path, workers=4), file_count=3)
    output = console.export_text()
    assert "Workers: 4" in output


def test_log_writer_writes_tsv(tmp_path: Path) -> None:
    log = tmp_path / "rename.log"
    with LogWriter(log) as writer:
        writer.write_event(
            action="copy",
            source=Path("/a/b.jpg"),
            destination=Path("/a/renamed/2026-08-01_14-55-22.jpg"),
            source_label="WhatsApp",
            origin="filesystem",
            message="",
        )
    text = log.read_text(encoding="utf-8")
    assert "copy" in text
    assert "b.jpg" in text
    assert "WhatsApp" in text
