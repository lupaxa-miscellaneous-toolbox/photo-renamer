"""Path and extension helpers for lupaxa.photo_renamer."""

from __future__ import annotations

from pathlib import Path

import platformdirs

from lupaxa.photo_renamer.constants import DEFAULT_EXTENSIONS


def normalize_extension(ext: str) -> str:
    """Return a lowercase extension without a leading dot."""
    return ext.lower().lstrip(".")


def is_supported_extension(
    ext: str,
    include: set[str] | None,
    exclude: set[str] | None,
) -> bool:
    """Return whether *ext* is allowed after applying include/exclude filters."""
    normalized = normalize_extension(ext)
    allowed = include if include is not None else set(DEFAULT_EXTENSIONS)
    allowed = {normalize_extension(e) for e in allowed}
    if normalized not in allowed:
        return False
    if exclude is not None and normalized in {normalize_extension(e) for e in exclude}:
        return False
    return True


def user_log_dir() -> Path:
    """Return the platform-specific log directory for this application."""
    return Path(
        platformdirs.user_log_dir(appname="lupaxa-photo-renamer", appauthor="Lupaxa")
    )
