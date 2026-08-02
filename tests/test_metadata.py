import os
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pytest
from PIL import ExifTags

from lupaxa.photo_renamer.metadata import (
    _read_image_exif_datetime,
    _read_video_datetime,
    extract_timestamp,
    parse_exif_datetime,
)


def test_parse_exif_datetime() -> None:
    assert parse_exif_datetime("2026:08:01 14:55:22") == datetime(2026, 8, 1, 14, 55, 22)


def test_image_exif_prefers_original_datetime(tmp_path: Path) -> None:
    path = tmp_path / "a.jpg"
    image = MagicMock()
    image.getexif.return_value = {
        306: "2024:01:01 01:01:01",
        36868: "2025:02:02 02:02:02",
        36867: "2026:03:03 03:03:03",
    }
    image.__enter__.return_value = image

    with patch("lupaxa.photo_renamer.metadata.Image.open", return_value=image):
        result = _read_image_exif_datetime(path)

    assert result == datetime(2026, 3, 3, 3, 3, 3)


def test_image_exif_prefers_original_datetime_from_exif_ifd(tmp_path: Path) -> None:
    path = tmp_path / "nested.jpg"
    exif = MagicMock()
    exif.__bool__.return_value = True
    exif.get.side_effect = lambda tag: {306: "2024:01:01 01:01:01"}.get(tag)
    exif.get_ifd.return_value = {
        36867: "2026:03:03 03:03:03",
        36868: "2025:02:02 02:02:02",
    }
    image = MagicMock()
    image.getexif.return_value = exif
    image.__enter__.return_value = image

    with patch("lupaxa.photo_renamer.metadata.Image.open", return_value=image):
        result = _read_image_exif_datetime(path)

    exif.get_ifd.assert_called_once_with(ExifTags.IFD.Exif)
    assert result == datetime(2026, 3, 3, 3, 3, 3)


def test_video_uses_mediainfo_encoded_date(tmp_path: Path) -> None:
    path = tmp_path / "a.mp4"
    media_info = SimpleNamespace(
        tracks=[
            SimpleNamespace(
                track_type="General",
                encoded_date="UTC 2026-08-01 14:55:22",
                tagged_date=None,
            )
        ]
    )

    with patch(
        "lupaxa.photo_renamer.metadata.MediaInfo.parse",
        return_value=media_info,
    ):
        result = _read_video_datetime(path)

    assert result == datetime(2026, 8, 1, 14, 55, 22, tzinfo=UTC)


def test_filesystem_mode_uses_mtime(tmp_path: Path) -> None:
    path = tmp_path / "a.jpg"
    path.write_bytes(b"not-a-real-jpeg")

    result = extract_timestamp(path, mode="filesystem", timezone=None)

    assert result.missing is False
    assert result.origin == "filesystem"
    assert result.value is not None


def test_filesystem_mtime_converts_from_local_to_target_timezone(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "a.jpg"
    path.write_bytes(b"x")
    timestamp = datetime(2026, 1, 15, 12, 0, tzinfo=UTC).timestamp()
    os.utime(path, (timestamp, timestamp))

    with monkeypatch.context() as context:
        context.setenv("TZ", "America/Los_Angeles")
        time.tzset()
        result = extract_timestamp(
            path,
            mode="filesystem",
            timezone=ZoneInfo("Europe/Berlin"),
        )
    time.tzset()

    assert result.value == datetime(2026, 1, 15, 13, 0)


def test_exif_mode_missing_without_fallback(tmp_path: Path) -> None:
    path = tmp_path / "a.jpg"
    path.write_bytes(b"x")
    with patch("lupaxa.photo_renamer.metadata._read_image_exif_datetime", return_value=None):
        result = extract_timestamp(path, mode="exif", timezone=None)

    assert result.missing is True
    assert result.value is None
    assert result.origin == "none"


def test_auto_falls_back_to_filesystem(tmp_path: Path) -> None:
    path = tmp_path / "a.jpg"
    path.write_bytes(b"x")
    with patch("lupaxa.photo_renamer.metadata._read_image_exif_datetime", return_value=None):
        result = extract_timestamp(path, mode="auto", timezone=None)

    assert result.missing is False
    assert result.origin == "filesystem"


def test_auto_uses_video_metadata_before_filesystem(tmp_path: Path) -> None:
    path = tmp_path / "a.mp4"
    path.write_bytes(b"x")
    metadata_value = datetime(2026, 8, 1, 14, 55, 22)
    with patch(
        "lupaxa.photo_renamer.metadata._read_video_datetime",
        return_value=metadata_value,
    ):
        result = extract_timestamp(path, mode="auto", timezone=None)

    assert result.value == metadata_value
    assert result.origin == "mediainfo"


def test_timezone_conversion_returns_naive_wall_time(tmp_path: Path) -> None:
    path = tmp_path / "a.jpg"
    path.write_bytes(b"x")
    metadata_value = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)
    with patch(
        "lupaxa.photo_renamer.metadata._read_image_exif_datetime",
        return_value=metadata_value,
    ):
        result = extract_timestamp(path, mode="auto", timezone=ZoneInfo("Europe/Berlin"))

    assert result.value == datetime(2026, 8, 1, 14, 0)
    assert result.value is not None
    assert result.value.tzinfo is None
