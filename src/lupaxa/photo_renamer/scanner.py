"""Media file discovery for lupaxa.photo_renamer."""

from __future__ import annotations

import os
from pathlib import Path

from lupaxa.photo_renamer.models import MediaFile
from lupaxa.photo_renamer.utils import is_supported_extension, normalize_extension


def _is_under_output(path: Path, output_dir: Path) -> bool:
    resolved = path.resolve()
    output = output_dir.resolve()
    if resolved == output:
        return True
    try:
        resolved.relative_to(output)
    except ValueError:
        return False
    return True


def _scan_dir(
    dir_path: Path,
    *,
    output_dir: Path,
    include: set[str] | None,
    exclude: set[str] | None,
    recursive: bool,
    results: list[MediaFile],
) -> None:
    if _is_under_output(dir_path, output_dir):
        return

    with os.scandir(dir_path) as entries:
        for entry in entries:
            entry_path = Path(entry.path)
            if entry.is_dir(follow_symlinks=False):
                if recursive and not _is_under_output(entry_path, output_dir):
                    _scan_dir(
                        entry_path,
                        output_dir=output_dir,
                        include=include,
                        exclude=exclude,
                        recursive=recursive,
                        results=results,
                    )
            elif entry.is_file(follow_symlinks=False):
                if _is_under_output(entry_path, output_dir):
                    continue
                extension = normalize_extension(entry_path.suffix)
                if not is_supported_extension(extension, include, exclude):
                    continue
                results.append(
                    MediaFile(
                        path=entry_path,
                        extension=extension,
                        size=entry.stat(follow_symlinks=False).st_size,
                    )
                )


def scan_media(
    root: Path,
    *,
    recursive: bool,
    output_dir: Path,
    include: set[str] | None,
    exclude: set[str] | None,
) -> list[MediaFile]:
    """Collect supported media files under *root*, skipping *output_dir*."""
    results: list[MediaFile] = []
    _scan_dir(
        root.resolve(),
        output_dir=output_dir,
        include=include,
        exclude=exclude,
        recursive=recursive,
        results=results,
    )
    return results
