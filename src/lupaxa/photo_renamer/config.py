"""Application configuration and command-line parsing."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Never, cast
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from lupaxa.photo_renamer.exceptions import ConfigError
from lupaxa.photo_renamer.models import NameFormat, TimestampMode
from lupaxa.photo_renamer.utils import DEFAULT_EXTENSIONS, normalize_extension


@dataclass(frozen=True)
class AppConfig:
    """Validated configuration for one photo-renamer run."""

    root: Path
    output_dir: Path
    recursive: bool
    dry_run: bool
    verbose: bool
    quiet: bool
    force: bool
    skip_existing: bool
    timestamp_mode: TimestampMode
    name_format: NameFormat
    organise: bool
    flatten: bool
    move: bool
    include: set[str] | None
    exclude: set[str] | None
    timezone: ZoneInfo | None
    log_file: Path | None


class _ArgumentParser(argparse.ArgumentParser):
    """Argument parser that reports invalid configuration consistently."""

    def error(self: _ArgumentParser, message: str) -> Never:
        raise ConfigError(message)


def _extension_set(value: str | None) -> set[str] | None:
    if value is None:
        return None
    return {normalize_extension(item.strip()) for item in value.split(",") if item.strip()}


def _timezone(value: str | None) -> ZoneInfo | None:
    if value is None:
        return None
    try:
        return ZoneInfo(value)
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise ConfigError(f"unknown timezone: {value}") from exc


def parse_args(argv: list[str] | None = None) -> AppConfig:
    """Parse command-line arguments into an immutable application config."""
    parser = _ArgumentParser(prog="photo-renamer")
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path, default=Path("renamed"))
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--timestamp", choices=("auto", "exif", "filesystem"), default="auto")
    parser.add_argument("--format", choices=("datetime", "source", "source-first"), default=None)
    parser.add_argument("--preserve-source", action="store_true")
    parser.add_argument("--organise", action="store_true")
    parser.add_argument("--flatten", action="store_true")
    parser.add_argument("--move", action="store_true")
    parser.add_argument("--include")
    parser.add_argument("--exclude")
    parser.add_argument("--timezone")
    parser.add_argument("--log-file", type=Path)
    args = parser.parse_args(argv)

    if args.quiet and args.verbose:
        raise ConfigError("--quiet and --verbose cannot be used together")

    root = cast(Path, args.path).resolve()
    if not root.is_dir():
        raise ConfigError(f"path is not an existing directory: {root}")

    output = cast(Path, args.output)
    output_dir = (root / output if not output.is_absolute() else output).resolve()
    selected_format = args.format or ("source" if args.preserve_source else "datetime")
    include = _extension_set(args.include)
    if include is not None:
        unsupported = include - DEFAULT_EXTENSIONS
        if unsupported:
            joined = ", ".join(sorted(unsupported))
            label = "extension" if len(unsupported) == 1 else "extensions"
            raise ConfigError(f"unsupported --include {label}: {joined}")

    return AppConfig(
        root=root,
        output_dir=output_dir,
        recursive=bool(args.recursive),
        dry_run=bool(args.dry_run),
        verbose=bool(args.verbose),
        quiet=bool(args.quiet),
        force=bool(args.force),
        skip_existing=bool(args.skip_existing),
        timestamp_mode=cast(TimestampMode, args.timestamp),
        name_format=cast(NameFormat, selected_format),
        organise=bool(args.organise),
        flatten=bool(args.flatten),
        move=bool(args.move),
        include=include,
        exclude=_extension_set(args.exclude),
        timezone=_timezone(args.timezone),
        log_file=cast(Path | None, args.log_file),
    )
