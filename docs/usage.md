# Usage

The command accepts a source directory as `PATH`:

```text
photo-renamer [options] PATH
```

## Recommended workflow

Preview a recursive run:

```bash
photo-renamer --dry-run --recursive ~/Pictures
```

Review the root, resolved output directory, operation, format, timestamp mode, and file count
shown in the startup panel. Remove `--dry-run` only when they are correct.

## Default behaviour

```bash
photo-renamer ~/Pictures
```

This scans supported media directly inside `~/Pictures`, copies each successful result to
`~/Pictures/renamed/`, and names it `YYYY-MM-DD_HH-MM-SS.ext`. Add `--recursive` to scan nested
directories. The output directory is always excluded from scanning.

Nested input directories are preserved by default:

```text
Pictures/holiday/day-1/photo.jpg
→ Pictures/renamed/holiday/day-1/2026-08-01_14-55-22.jpg
```

Use `--move` to remove successfully processed source files. A failure affects only that file,
but causes a non-zero process exit code.

## Selecting files

Supported extensions are:

- Images: `jpg`, `jpeg`, `png`, `heic`, `heif`, `webp`, `tif`, `tiff`
- Videos: `mp4`, `mov`, `avi`, `mkv`, `m4v`, `3gp`

Extension matching is case-insensitive. Comma-separated filters narrow the supported set:

```bash
photo-renamer --recursive --include jpg,jpeg,heic ~/Pictures
photo-renamer --recursive --exclude mov,mp4 ~/Pictures
```

## Naming

Choose among three formats:

```bash
photo-renamer --format datetime ~/Pictures
photo-renamer --format source ~/Pictures
photo-renamer --format source-first ~/Pictures
```

`--preserve-source` is an alias for `--format source`. If both are supplied, an explicit
`--format` value takes precedence.

Use `--skip-existing` to skip filenames already matching a generated date-based pattern.
Adding `--force` processes those files instead.

## Output and logging

A relative `--output` is resolved below `PATH`; an absolute path is used as given:

```bash
photo-renamer --output sorted ~/Pictures
photo-renamer --output /Volumes/Archive ~/Pictures
```

`--log-file PATH` appends tab-separated audit events during real runs. Dry runs do not write
the log.

Use `--verbose` for per-file actions or `--quiet` to suppress Rich output. They cannot be used
together.
