"""Output path organisation for renamed media files."""

from __future__ import annotations

from pathlib import Path


def resolve_destination_dir(
    *,
    root: Path,
    output_dir: Path,
    source_file: Path,
    detected_source: str,
    organise: bool,
    flatten: bool,
) -> Path:
    """Return the destination directory for a renamed file."""
    root = root.resolve()
    source_file = source_file.resolve()
    rel_parent = source_file.relative_to(root).parent
    parts: list[str] = []
    if not flatten and rel_parent != Path("."):
        parts.extend(rel_parent.parts)
    if organise:
        parts.append(detected_source)
    return output_dir.joinpath(*parts) if parts else output_dir
