"""Tests for reporting helpers and log file writer."""

from __future__ import annotations

from pathlib import Path

from lupaxa.photo_renamer.reporting import LogWriter


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
