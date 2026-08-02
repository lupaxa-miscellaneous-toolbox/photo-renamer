"""Date-based filename builders and already-named detection."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from lupaxa.photo_renamer.models import NameFormat
from lupaxa.photo_renamer.utils import normalize_extension

ALREADY_NAMED_RE = re.compile(
    r"^(?:"
    r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(?:_\d{3})?(?:_[A-Za-z][A-Za-z0-9]*(?:_\d{3})?)?"
    r"|"
    r"[A-Za-z][A-Za-z0-9]*_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(?:_\d{3})?"
    r")$"
)


def format_timestamp(dt: datetime) -> str:
    """Return *dt* as ``YYYY-MM-DD_HH-MM-SS``."""
    return dt.strftime("%Y-%m-%d_%H-%M-%S")


def build_filename(
    dt: datetime,
    extension: str,
    name_format: NameFormat,
    source: str,
) -> str:
    """Build a renamed filename from timestamp, extension, format, and source."""
    stamp = format_timestamp(dt)
    ext = normalize_extension(extension)
    if name_format == "datetime":
        stem = stamp
    elif name_format == "source":
        stem = f"{stamp}_{source}"
    elif name_format == "source-first":
        stem = f"{source}_{stamp}"
    else:
        msg = f"Unknown name format: {name_format}"
        raise ValueError(msg)
    return f"{stem}.{ext}"


def is_already_named(filename: str) -> bool:
    """Return whether *filename* already matches a date-based rename pattern."""
    return bool(ALREADY_NAMED_RE.match(Path(filename).stem))
