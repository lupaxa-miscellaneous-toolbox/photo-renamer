"""Command-line interface for lupaxa.photo_renamer."""

from __future__ import annotations

import sys

from lupaxa.photo_renamer.config import AppConfig, parse_args
from lupaxa.photo_renamer.exceptions import ConfigError


def parse_arguments(argv: list[str] | None = None) -> AppConfig:
    """Parse CLI arguments into application configuration."""
    return parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments; pipeline execution is wired in a later task."""
    try:
        parse_arguments(argv)
    except ConfigError as exc:
        print(exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
