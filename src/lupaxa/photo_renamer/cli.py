"""Command-line interface for lupaxa.photo_renamer."""

from __future__ import annotations

import sys

from rich.console import Console

from lupaxa.photo_renamer.config import AppConfig, parse_args
from lupaxa.photo_renamer.exceptions import ConfigError
from lupaxa.photo_renamer.pipeline import run


def parse_arguments(argv: list[str] | None = None) -> AppConfig:
    """Parse CLI arguments into application configuration."""
    return parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the rename pipeline and map its outcome to a process exit code."""
    try:
        config = parse_arguments(argv)
    except ConfigError as exc:
        print(exc, file=sys.stderr)
        return 2
    stats = run(config, console=Console(quiet=config.quiet))
    return 1 if stats.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
