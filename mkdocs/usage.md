# Usage

```text
photo-renamer [options] PATH
```

`PATH` is the directory to scan.

## Recommended workflow

```bash
photo-renamer --dry-run --recursive ~/Pictures
```

Review the startup panel (root, output, operation, format, timestamp mode, file
count). Remove `--dry-run` only when those values are correct.

## Default behaviour

```bash
photo-renamer ~/Pictures
```

This scans supported media directly inside `~/Pictures`, copies each successful
result to `~/Pictures/renamed/`, and names it `YYYY-MM-DD_HH-MM-SS.ext`. Add
`--recursive` for nested directories. The output directory is always excluded
from scanning.

Nested input directories are preserved by default:

```text
Pictures/holiday/day-1/photo.jpg
→ Pictures/renamed/holiday/day-1/2026-08-01_14-55-22.jpg
```

Use `--move` to remove successfully processed source files. A failure affects
only that file, but causes a non-zero process exit code.

## Selecting files

```bash
photo-renamer --recursive --include jpg,jpeg,heic ~/Pictures
photo-renamer --recursive --exclude mov,mp4 ~/Pictures
```

## Naming

```bash
photo-renamer --format datetime ~/Pictures
photo-renamer --format source ~/Pictures
photo-renamer --format source-first ~/Pictures
```

`--preserve-source` is an alias for `--format source`. If both are supplied, an
explicit `--format` value takes precedence.

Use `--skip-existing` to skip filenames already matching a generated date-based
pattern. Adding `--force` processes those files instead.

## Organising media

Assume this input:

```text
PATH/vacation/day-1/IMG-20260801-WA0001.jpg
```

| Options                 | Destination below output                              |
| ----------------------- | ----------------------------------------------------- |
| none                    | `vacation/day-1/2026-08-01_14-55-22.jpg`              |
| `--organise`            | `vacation/day-1/WhatsApp/2026-08-01_14-55-22.jpg`     |
| `--flatten`             | `2026-08-01_14-55-22.jpg`                             |
| `--flatten --organise`  | `WhatsApp/2026-08-01_14-55-22.jpg`                    |

`--organise` nests the detected source **inside** the preserved relative path.

## Output and logging

```bash
photo-renamer --output sorted ~/Pictures
photo-renamer --output /Volumes/Archive ~/Pictures
photo-renamer --recursive --log-file ./rename-events.tsv ~/Pictures
```

A relative `--output` resolves below `PATH`. `--log-file` appends tab-separated
audit events on real runs (not dry runs).

Use `--verbose` for per-file actions or `--quiet` to suppress Rich output. They
cannot be used together.

## Troubleshooting

### No files are scanned

- Add `--recursive` if media is below nested directories
- Check `--include` / `--exclude` filters
- Files inside the resolved output directory are ignored
- Symlinks are not followed

### Missing metadata

`--timestamp exif` requires embedded EXIF or MediaInfo dates. Use `auto` for
filesystem fallback, or `filesystem` to always use modification time.

### Unexpected times

Inspect origins with `--verbose` and `--log-file`. Pass an IANA zone:

```bash
photo-renamer --timezone Europe/London --dry-run PATH
```

### A `_001` suffix appears

The destination already existed or was reserved in the same run. Suffixing
prevents overwrites.

## FAQ

**Are originals preserved?**  
Yes, by default. Only `--move` removes successfully processed sources.

**Does `--preserve-source` preserve originals?**  
No. It is a naming alias for `--format source`.

**Can it overwrite a file?**  
No. Unique suffixes and exclusive destination creation prevent overwrites.

**Is there an undo command?**  
Not in v1. Prefer `--dry-run`, copy mode, and `--log-file`.
