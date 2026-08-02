"""Worker-count helpers and over-cap confirmation."""

from __future__ import annotations

import os
import sys
from typing import TextIO

from lupaxa.photo_renamer.exceptions import ConfigError


def recommended_max_workers() -> int:
    """Return the soft recommended maximum: CPU count × 2."""
    return (os.cpu_count() or 1) * 2


def confirm_workers(
    workers: int,
    *,
    assume_yes: bool,
    stdin: TextIO | None = None,
    stderr: TextIO | None = None,
) -> None:
    """Confirm when *workers* exceeds the recommended maximum."""
    limit = recommended_max_workers()
    if workers <= limit or assume_yes:
        return

    in_stream = stdin if stdin is not None else sys.stdin
    err_stream = stderr if stderr is not None else sys.stderr
    message = f"Workers {workers} exceeds recommended max {limit} (CPU×2). Continue? [y/N] "

    if not in_stream.isatty():
        raise ConfigError(
            f"workers {workers} exceeds recommended max {limit} (CPU×2); "
            "re-run with --yes to confirm"
        )

    err_stream.write(message)
    err_stream.flush()
    try:
        answer = in_stream.readline()
    except EOFError as exc:
        raise ConfigError("workers confirmation cancelled") from exc
    if answer is None or answer.strip().lower() not in {"y", "yes"}:
        raise ConfigError("workers confirmation cancelled")
