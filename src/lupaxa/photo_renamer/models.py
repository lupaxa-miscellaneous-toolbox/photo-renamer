"""Core dataclasses and type aliases for lupaxa.photo_renamer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

TimestampOrigin = Literal["exif", "mediainfo", "filesystem", "none"]
NameFormat = Literal["datetime", "source", "source-first"]
TimestampMode = Literal["auto", "exif", "filesystem"]
PlanAction = Literal["copy", "move", "skip"]


@dataclass(frozen=True)
class MediaFile:
    """A media file discovered during scanning."""

    path: Path
    extension: str
    size: int


@dataclass(frozen=True)
class TimestampResult:
    """Resolved capture timestamp and its provenance."""

    value: datetime | None
    origin: TimestampOrigin
    missing: bool


@dataclass(frozen=True)
class RenamePlan:
    """Planned rename operation for a single media file."""

    source: Path
    destination: Path
    detected_source: str
    timestamp: TimestampResult
    action: PlanAction
    skipped_reason: str | None


@dataclass
class RunStats:
    """Mutable counters aggregated over a rename run."""

    scanned: int = 0
    processed: int = 0
    skipped: int = 0
    failed: int = 0
    collisions: int = 0
    metadata_missing: int = 0
