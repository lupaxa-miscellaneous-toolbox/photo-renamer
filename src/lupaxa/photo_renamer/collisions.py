"""Collision-safe destination path allocation."""

from __future__ import annotations

from pathlib import Path


def ensure_unique(
    destination: Path,
    *,
    reserved: set[Path] | None = None,
) -> tuple[Path, bool]:
    """Return a unique path, suffixing with _001, _002, … when needed."""
    reserved = reserved or set()

    def taken(path: Path) -> bool:
        return path.exists() or path.resolve() in reserved

    if not taken(destination):
        return destination, False
    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    n = 1
    while True:
        candidate = parent / f"{stem}_{n:03d}{suffix}"
        if not taken(candidate):
            return candidate, True
        n += 1
