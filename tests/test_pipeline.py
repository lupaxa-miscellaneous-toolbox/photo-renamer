"""End-to-end tests for planning and executing rename operations."""

from __future__ import annotations

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Self
from unittest.mock import patch

import pytest
from rich.console import Console

from lupaxa.photo_renamer.config import AppConfig
from lupaxa.photo_renamer.models import MediaFile, RenamePlan, TimestampResult
from lupaxa.photo_renamer.pipeline import plan_file, run
from lupaxa.photo_renamer.rename import apply_plan
from lupaxa.photo_renamer.scanner import ScanError


def _cfg(root: Path, **kwargs: object) -> AppConfig:
    base = {
        "root": root.resolve(),
        "output_dir": (root / "renamed").resolve(),
        "recursive": False,
        "dry_run": False,
        "verbose": False,
        "quiet": True,
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


def _timestamp() -> TimestampResult:
    return TimestampResult(
        value=datetime(2026, 8, 1, 13, 45, 22),
        origin="filesystem",
        missing=False,
    )


def test_copy_preserves_original(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"abc")
    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=_timestamp()):
        stats = run(_cfg(tmp_path))
    assert stats.processed == 1
    assert src.exists()
    dest = tmp_path / "renamed" / "2026-08-01_13-45-22.jpg"
    assert dest.exists()
    assert dest.read_bytes() == b"abc"


def test_move_removes_original(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"abc")
    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=_timestamp()):
        stats = run(_cfg(tmp_path, move=True))
    assert stats.processed == 1
    assert not src.exists()
    assert (tmp_path / "renamed" / "2026-08-01_13-45-22.jpg").exists()


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"abc")
    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=_timestamp()):
        stats = run(_cfg(tmp_path, dry_run=True))
    assert stats.processed == 1
    assert src.exists()
    assert not (tmp_path / "renamed").exists()


def test_plan_file_reserves_resolved_unique_destination(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"abc")
    media = MediaFile(path=src, extension="jpg", size=3)
    reserved = {(tmp_path / "renamed" / "2026-08-01_13-45-22.jpg").resolve()}
    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=_timestamp()):
        plan = plan_file(media, _cfg(tmp_path), reserved)
    assert plan.destination.name == "2026-08-01_13-45-22_001.jpg"
    assert plan.destination.resolve() in reserved


def test_missing_required_timestamp_is_failed(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"abc")
    missing = TimestampResult(value=None, origin="none", missing=True)
    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=missing):
        stats = run(_cfg(tmp_path, timestamp_mode="exif"))
    assert stats.failed == 1
    assert stats.metadata_missing == 1
    assert stats.processed == 0
    assert not (tmp_path / "renamed").exists()


def test_skip_existing_avoids_metadata_lookup(tmp_path: Path) -> None:
    src = tmp_path / "2026-08-01_13-45-22.jpg"
    src.write_bytes(b"abc")
    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp") as extract:
        stats = run(_cfg(tmp_path, skip_existing=True))
    assert stats.skipped == 1
    extract.assert_not_called()


def test_collision_is_counted_and_never_overwritten(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"new")
    output = tmp_path / "renamed"
    output.mkdir()
    existing = output / "2026-08-01_13-45-22.jpg"
    existing.write_bytes(b"old")
    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=_timestamp()):
        stats = run(_cfg(tmp_path))
    assert stats.collisions == 1
    assert existing.read_bytes() == b"old"
    assert (output / "2026-08-01_13-45-22_001.jpg").read_bytes() == b"new"


@pytest.mark.parametrize("action", ["copy", "move"])
def test_apply_plan_refuses_dangling_symlink_destination(tmp_path: Path, action: str) -> None:
    source = tmp_path / "photo.jpg"
    source.write_bytes(b"new")
    destination = tmp_path / "renamed.jpg"
    missing_target = tmp_path / "missing.jpg"
    destination.symlink_to(missing_target)
    plan = RenamePlan(
        source=source,
        destination=destination,
        detected_source="Camera",
        timestamp=_timestamp(),
        action=action,  # type: ignore[arg-type]
        skipped_reason=None,
    )

    with pytest.raises(FileExistsError):
        apply_plan(plan, dry_run=False)

    assert destination.is_symlink()
    assert destination.readlink() == missing_target
    assert not missing_target.exists()


def test_apply_plan_move_refuses_destination_claimed_during_link(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "photo.jpg"
    source.write_bytes(b"source")
    destination = tmp_path / "renamed" / "photo.jpg"
    plan = RenamePlan(
        source=source,
        destination=destination,
        detected_source="Camera",
        timestamp=_timestamp(),
        action="move",
        skipped_reason=None,
    )
    original_link = os.link

    def link_after_competitor(
        source_path: Path,
        destination_path: Path,
        *args: object,
        **kwargs: object,
    ) -> None:
        destination_path.write_bytes(b"racer")
        original_link(source_path, destination_path, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(os, "link", link_after_competitor)

    with pytest.raises(FileExistsError):
        apply_plan(plan, dry_run=False)

    assert source.read_bytes() == b"source"
    assert destination.read_bytes() == b"racer"


def test_operation_failure_is_counted_and_logged(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"abc")
    log_file = tmp_path / "events" / "rename.log"
    with (
        patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=_timestamp()),
        patch("lupaxa.photo_renamer.pipeline.apply_plan", side_effect=OSError("disk full")),
    ):
        stats = run(_cfg(tmp_path, log_file=log_file))
    assert stats.failed == 1
    assert stats.processed == 0
    log = log_file.read_text(encoding="utf-8")
    assert "\tfailed\t" in log
    assert "disk full" in log


def test_scan_error_is_counted_as_failure(tmp_path: Path) -> None:
    unreadable = tmp_path / "unreadable"

    def scan_with_error(
        *args: object,
        errors: list[ScanError],
        **kwargs: object,
    ) -> list[MediaFile]:
        errors.append(ScanError(path=unreadable, message="permission denied"))
        return []

    with patch("lupaxa.photo_renamer.pipeline.scan_media", side_effect=scan_with_error):
        stats = run(_cfg(tmp_path, recursive=True))

    assert stats.failed == 1
    assert stats.scanned == 0


def test_dry_run_does_not_create_log_file(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"abc")
    log_file = tmp_path / "rename.log"
    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=_timestamp()):
        run(_cfg(tmp_path, dry_run=True, log_file=log_file))
    assert not log_file.exists()


def test_workers_two_processes_all_files(tmp_path: Path) -> None:
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    for root in (root_a, root_b):
        root.mkdir()
        for index in range(5):
            (root / f"photo-{index}.jpg").write_bytes(f"data-{index}".encode())

    def fake_timestamp(path: Path, *args: object, **kwargs: object) -> TimestampResult:
        stamp = int(path.stem.split("-")[1])
        return TimestampResult(
            value=datetime(2026, 8, 1, 13, 45, stamp),
            origin="filesystem",
            missing=False,
        )

    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", side_effect=fake_timestamp):
        stats_one = run(_cfg(root_a, workers=1))
        stats_two = run(_cfg(root_b, workers=2))

    names_one = sorted(p.name for p in (root_a / "renamed").glob("*.jpg"))
    names_two = sorted(p.name for p in (root_b / "renamed").glob("*.jpg"))
    assert names_one == names_two
    assert stats_one.processed == stats_two.processed == 5
    assert stats_one.failed == stats_two.failed == 0


def test_workers_two_processes_all_files_with_collisions(tmp_path: Path) -> None:
    """workers=1 and workers=2 must resolve identical collisions on shared timestamps."""
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    file_count = 6
    for root in (root_a, root_b):
        root.mkdir()
        for index in range(file_count):
            (root / f"photo-{index}.jpg").write_bytes(f"data-{index}".encode())

    def fake_timestamp(path: Path, *args: object, **kwargs: object) -> TimestampResult:
        # Two groups of three files share a timestamp each, forcing collisions.
        stamp = int(path.stem.split("-")[1])
        group_second = 0 if stamp < 3 else 1
        return TimestampResult(
            value=datetime(2026, 8, 1, 13, 45, group_second),
            origin="filesystem",
            missing=False,
        )

    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", side_effect=fake_timestamp):
        stats_one = run(_cfg(root_a, workers=1))
        stats_two = run(_cfg(root_b, workers=2))

    names_one = sorted(p.name for p in (root_a / "renamed").glob("*.jpg"))
    names_two = sorted(p.name for p in (root_b / "renamed").glob("*.jpg"))
    assert names_one == names_two
    assert stats_one.processed == stats_two.processed == file_count
    assert stats_one.failed == stats_two.failed == 0
    # Two groups of three colliding files each contribute two collisions.
    assert stats_one.collisions == stats_two.collisions == 4


def test_keyboard_interrupt_aborts_apply_phase(tmp_path: Path) -> None:
    """Ctrl-C during apply must cancel pending work instead of draining the queue."""
    file_count = 40
    for index in range(file_count):
        (tmp_path / f"photo-{index:03d}.jpg").write_bytes(f"data-{index}".encode())

    def fake_timestamp(path: Path, *args: object, **kwargs: object) -> TimestampResult:
        stamp = int(path.stem.split("-")[1])
        return TimestampResult(
            value=datetime(2026, 8, 1, 13, 45, stamp % 60),
            origin="filesystem",
            missing=False,
        )

    call_count = 0

    def flaky_apply(plan: RenamePlan, *, dry_run: bool) -> None:
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise KeyboardInterrupt
        time.sleep(0.01)
        apply_plan(plan, dry_run=dry_run)

    with (
        patch("lupaxa.photo_renamer.pipeline.extract_timestamp", side_effect=fake_timestamp),
        patch("lupaxa.photo_renamer.pipeline.apply_plan", side_effect=flaky_apply),
        pytest.raises(KeyboardInterrupt),
    ):
        run(_cfg(tmp_path, workers=1))

    destinations = list((tmp_path / "renamed").glob("*.jpg"))
    assert len(destinations) < file_count // 2


def test_pipeline_uses_planning_then_apply_progress(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"abc")
    descriptions: list[str] = []

    class FakeProgress:
        def __enter__(self: Self) -> Self:
            return self

        def __exit__(self: Self, *args: object) -> None:
            return None

        @property
        def task_ids(self: Self) -> list[int]:
            return [0]

        def advance(self: Self, task_id: int) -> None:
            return None

    def fake_make_progress(console: object, total: int, description: str) -> FakeProgress:
        descriptions.append(description)
        return FakeProgress()

    with (
        patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=_timestamp()),
        patch("lupaxa.photo_renamer.pipeline.make_progress", side_effect=fake_make_progress),
    ):
        run(_cfg(tmp_path, quiet=False, workers=1), console=Console(quiet=True))

    assert descriptions == ["Planning media", "Copying media"]


def test_apply_phase_description_for_move_and_dry_run(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"abc")
    descriptions: list[str] = []

    def fake_make_progress(console: object, total: int, description: str) -> object:
        descriptions.append(description)

        class _P:
            def __enter__(self: Self) -> Self:
                return self

            def __exit__(self: Self, *args: object) -> None:
                return None

            @property
            def task_ids(self: Self) -> list[int]:
                return [0]

            def advance(self: Self, task_id: int) -> None:
                return None

        return _P()

    with (
        patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=_timestamp()),
        patch("lupaxa.photo_renamer.pipeline.make_progress", side_effect=fake_make_progress),
    ):
        run(_cfg(tmp_path, quiet=False, move=True), console=Console(quiet=True))
        run(_cfg(tmp_path, quiet=False, dry_run=True), console=Console(quiet=True))

    assert "Moving media" in descriptions
    assert "Dry-run apply" in descriptions


def test_verbose_prints_file_action_and_quiet_suppresses_output(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"abc")
    verbose_console = Console(record=True, width=120)
    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=_timestamp()):
        run(_cfg(tmp_path, quiet=False, verbose=True, dry_run=True), console=verbose_console)
    output = verbose_console.export_text()
    assert "copy" in output
    assert src.name in output

    quiet_console = Console(record=True, width=120)
    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=_timestamp()):
        run(_cfg(tmp_path, quiet=True, verbose=False, dry_run=True), console=quiet_console)
    assert quiet_console.export_text() == ""
