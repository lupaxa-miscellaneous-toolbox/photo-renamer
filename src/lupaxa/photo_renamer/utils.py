"""Path and extension helpers for lupaxa.photo_renamer."""

from __future__ import annotations

from pathlib import Path

import platformdirs

from lupaxa.photo_renamer.constants import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS

DEFAULT_EXTENSIONS: frozenset[str] = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


def path_is_taken(path: Path) -> bool:
    """Return whether *path* names an existing entry, including dangling symlinks."""
    return path.exists() or path.is_symlink()


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
    allowed = set(DEFAULT_EXTENSIONS)
    if include is not None:
        allowed &= {normalize_extension(e) for e in include}
    return normalized in allowed and (
        exclude is None or normalized not in {normalize_extension(e) for e in exclude}
    )


def user_log_dir() -> Path:
    """Return the platform-specific log directory for this application."""
    return Path(platformdirs.user_log_dir(appname="lupaxa-photo-renamer", appauthor="Lupaxa"))
