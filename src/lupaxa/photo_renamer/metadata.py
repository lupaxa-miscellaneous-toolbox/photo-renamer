"""Extract image, video, and filesystem timestamps."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from PIL import Image
from pymediainfo import MediaInfo

from lupaxa.photo_renamer.constants import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
from lupaxa.photo_renamer.models import TimestampMode, TimestampOrigin, TimestampResult

try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
except (ImportError, OSError):
    pass

_EXIF_DATETIME_TAGS = (36867, 36868, 306)
_MEDIAINFO_DATETIME_FIELDS = (
    "recorded_date",
    "file_creation_date",
    "file_creation_date__local",
    "encoded_date",
    "tagged_date",
)


def parse_exif_datetime(value: str) -> datetime | None:
    """Parse an EXIF ``YYYY:MM:DD HH:MM:SS`` value."""
    try:
        return datetime.strptime(value.strip().strip("\x00"), "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None


def _read_image_exif_datetime(path: Path) -> datetime | None:
    """Return the highest-priority EXIF timestamp from *path*, if available."""
    try:
        with Image.open(path) as image:
            exif = image.getexif()
            if not exif:
                legacy_getexif = getattr(image, "_getexif", None)
                exif = legacy_getexif() if callable(legacy_getexif) else None
            if not exif:
                return None
            for tag in _EXIF_DATETIME_TAGS:
                raw_value = exif.get(tag)
                if isinstance(raw_value, bytes):
                    raw_value = raw_value.decode("ascii", errors="ignore")
                if isinstance(raw_value, str):
                    parsed = parse_exif_datetime(raw_value)
                    if parsed is not None:
                        return parsed
    except (OSError, TypeError, ValueError):
        return None
    return None


def _parse_mediainfo_datetime(value: str) -> datetime | None:
    """Parse common MediaInfo date representations."""
    normalized = value.strip().strip("\x00")
    is_utc = normalized.startswith("UTC ")
    if is_utc:
        normalized = normalized.removeprefix("UTC ")
    if normalized.endswith(" UTC"):
        normalized = normalized.removesuffix(" UTC")
        is_utc = True
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if is_utc and parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _read_video_datetime(path: Path) -> datetime | None:
    """Return the first creation or encoded timestamp reported by MediaInfo."""
    try:
        media_info = MediaInfo.parse(path)
        tracks: list[Any] = media_info.tracks
        ordered_tracks = sorted(
            tracks,
            key=lambda track: getattr(track, "track_type", None) != "General",
        )
        for track in ordered_tracks:
            for field in _MEDIAINFO_DATETIME_FIELDS:
                raw_value = getattr(track, field, None)
                if isinstance(raw_value, str) and raw_value:
                    parsed = _parse_mediainfo_datetime(raw_value)
                    if parsed is not None:
                        return parsed
    except Exception:
        return None
    return None


def _apply_timezone(value: datetime, timezone: ZoneInfo | None) -> datetime:
    """Convert *value* to *timezone* and return naive wall-clock components."""
    if timezone is None:
        return value
    value = (
        value.replace(tzinfo=timezone)
        if value.tzinfo is None
        else value.astimezone(timezone)
    )
    return value.replace(tzinfo=None)


def _filesystem_timestamp(path: Path) -> datetime:
    """Return *path*'s filesystem modification time."""
    return datetime.fromtimestamp(path.stat().st_mtime)


def extract_timestamp(
    path: Path,
    mode: TimestampMode,
    timezone: ZoneInfo | None,
) -> TimestampResult:
    """Resolve a timestamp according to media type, mode, and target timezone."""
    value: datetime | None = None
    origin: TimestampOrigin = "none"
    extension = path.suffix.lower().lstrip(".")

    if mode != "filesystem":
        if extension in IMAGE_EXTENSIONS:
            value = _read_image_exif_datetime(path)
            origin = "exif" if value is not None else "none"
        elif extension in VIDEO_EXTENSIONS:
            value = _read_video_datetime(path)
            origin = "mediainfo" if value is not None else "none"

    if value is None and mode != "exif":
        value = _filesystem_timestamp(path)
        origin = "filesystem"

    if value is None:
        return TimestampResult(value=None, origin="none", missing=True)
    return TimestampResult(
        value=_apply_timezone(value, timezone),
        origin=origin,
        missing=False,
    )
