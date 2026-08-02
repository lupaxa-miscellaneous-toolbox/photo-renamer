"""Command-line interface for lupaxa.photo_renamer."""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Fully implemented in a later task."""
    _ = argv
    print("photo-renamer: not implemented yet", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
