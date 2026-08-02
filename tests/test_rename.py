import errno
import os
from datetime import datetime
from pathlib import Path

import pytest

from lupaxa.photo_renamer.models import RenamePlan, TimestampResult
from lupaxa.photo_renamer.rename import apply_plan, build_filename, is_already_named


def test_build_filename_formats() -> None:
    dt = datetime(2026, 8, 1, 14, 55, 22)
    assert build_filename(dt, "JPG", "datetime", "WhatsApp") == "2026-08-01_14-55-22.jpg"
    assert build_filename(dt, "jpg", "source", "WhatsApp") == "2026-08-01_14-55-22_WhatsApp.jpg"
    assert (
        build_filename(dt, "jpg", "source-first", "WhatsApp") == "WhatsApp_2026-08-01_14-55-22.jpg"
    )


def test_is_already_named() -> None:
    assert is_already_named("2026-08-01_14-55-22.jpg") is True
    assert is_already_named("2026-08-01_14-55-22_001.jpg") is True
    assert is_already_named("2026-08-01_14-55-22_WhatsApp.jpg") is True
    assert is_already_named("2026-08-01_14-55-22_001_WhatsApp.jpg") is True
    assert is_already_named("2026-08-01_14-55-22_WhatsApp_001.jpg") is True
    assert is_already_named("WhatsApp_2026-08-01_14-55-22.jpg") is True
    assert is_already_named("WhatsApp_2026-08-01_14-55-22_001.jpg") is True
    assert is_already_named("IMG-20260801-WA0001.jpg") is False


@pytest.mark.parametrize("error_number", [errno.EPERM, errno.EOPNOTSUPP, errno.ENOSYS])
def test_move_falls_back_to_exclusive_copy_for_unsupported_link(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error_number: int,
) -> None:
    source = tmp_path / "source.jpg"
    source.write_bytes(b"photo")
    destination = tmp_path / "destination.jpg"
    plan = RenamePlan(
        source=source,
        destination=destination,
        detected_source="Camera",
        timestamp=TimestampResult(
            value=datetime(2026, 8, 1, 14, 55, 22),
            origin="filesystem",
            missing=False,
        ),
        action="move",
        skipped_reason=None,
    )

    def unsupported_link(*args: object, **kwargs: object) -> None:
        raise OSError(error_number, os.strerror(error_number))

    monkeypatch.setattr(os, "link", unsupported_link)
    apply_plan(plan, dry_run=False)

    assert destination.read_bytes() == b"photo"
    assert not source.exists()
