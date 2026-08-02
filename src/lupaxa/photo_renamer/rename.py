"""Date-based filename builders and already-named detection."""

from __future__ import annotations

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

from lupaxa.photo_renamer.models import NameFormat, RenamePlan
from lupaxa.photo_renamer.utils import normalize_extension, path_is_taken

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


def _move_exclusive(source: Path, destination: Path) -> None:
    """Move *source* after exclusively claiming *destination*."""
    descriptor = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        placeholder = os.fstat(descriptor)
    finally:
        os.close(descriptor)

    try:
        os.replace(source, destination)
    except OSError:
        try:
            current = os.lstat(destination)
        except FileNotFoundError:
            pass
        else:
            if (current.st_dev, current.st_ino) == (placeholder.st_dev, placeholder.st_ino):
                destination.unlink()
        raise


def apply_plan(plan: RenamePlan, *, dry_run: bool) -> None:
    """Apply one copy or move plan without overwriting an existing file."""
    if dry_run or plan.action == "skip":
        return
    if path_is_taken(plan.destination):
        msg = f"destination already exists: {plan.destination}"
        raise FileExistsError(msg)

    plan.destination.parent.mkdir(parents=True, exist_ok=True)
    if plan.action == "copy":
        with plan.source.open("rb") as source, plan.destination.open("xb") as destination:
            shutil.copyfileobj(source, destination)
        shutil.copystat(plan.source, plan.destination)
    else:
        _move_exclusive(plan.source, plan.destination)
