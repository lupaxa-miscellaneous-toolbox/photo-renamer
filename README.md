# lupaxa-photo-renamer

`lupaxa-photo-renamer` safely copies or moves photographs and videos into consistent,
date-based filenames. It reads image EXIF or video metadata when available, falls back to
filesystem modification time in the default mode, detects common source apps, and reports
progress with [Rich](https://github.com/Textualize/rich).

> A Rich terminal screenshot will be added under `docs/assets/`. Until then, the startup
> panel, progress bar, and summary table are shown directly in your terminal.

## Installation

Python 3.13 or newer is required.

```bash
pip install lupaxa-photo-renamer
```

For local development:

```bash
git clone https://github.com/lupaxa-code-playground/photo-renamer.git
cd photo-renamer
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Video timestamp extraction uses MediaInfo. If it is unavailable on your system, install the
MediaInfo package with your operating system's package manager.

## Quick start

Preview the work first:

```bash
photo-renamer --dry-run --recursive ~/Pictures
```

Then run the same command without `--dry-run`:

```bash
photo-renamer --recursive ~/Pictures
```

By default, files are **copied**, originals remain untouched, and results are written below
`PATH/renamed/`. Existing relative directories are preserved:

```text
Pictures/holiday/day-1/IMG-20260801-WA0001.JPG
→ Pictures/renamed/holiday/day-1/2026-08-01_14-55-22.jpg
```

Use `--move` only when you intentionally want to remove each successfully processed source.

## Common examples

```bash
# Include a detected source label in each filename
photo-renamer --recursive --format source ~/Pictures

# --preserve-source is an alias for --format source
photo-renamer --preserve-source ~/Pictures

# Put a source folder inside each preserved relative path
photo-renamer --recursive --organise ~/Pictures
# → renamed/holiday/day-1/WhatsApp/2026-08-01_14-55-22.jpg

# Drop relative paths, retaining only source folders
photo-renamer --recursive --flatten --organise ~/Pictures
# → renamed/WhatsApp/2026-08-01_14-55-22.jpg

# Choose another output root and move instead of copy
photo-renamer --recursive --output /Volumes/Archive --move ~/Pictures
```

## Flag summary

| Flag | Purpose |
| --- | --- |
| `--output DIR` | Output root; defaults to `renamed` under `PATH` |
| `--recursive` | Scan subdirectories; off by default |
| `--dry-run` | Plan and report without writing |
| `--move` | Move files instead of copying |
| `--timestamp auto\|exif\|filesystem` | Select the timestamp strategy |
| `--format datetime\|source\|source-first` | Select the filename format |
| `--preserve-source` | Alias for `--format source` |
| `--organise` | Nest the detected source inside the relative path |
| `--flatten` | Remove relative path segments from destinations |
| `--include EXT,...` | Process only listed supported extensions |
| `--exclude EXT,...` | Exclude listed extensions |
| `--skip-existing` | Skip files already matching a target naming pattern |
| `--force` | Process matching names even with `--skip-existing` |
| `--timezone ZONE` | Convert timestamps to an IANA zone before naming |
| `--log-file PATH` | Append a tab-separated audit log |
| `--verbose` / `--quiet` | Increase or suppress terminal output |

Run `photo-renamer --help` for the authoritative command syntax.

## Filename formats

- `datetime` (default): `2026-08-01_14-55-22.jpg`
- `source`: `2026-08-01_14-55-22_WhatsApp.jpg`
- `source-first`: `WhatsApp_2026-08-01_14-55-22.jpg`

Extensions are preserved and lowercased.

## Supported formats

**Images:** JPG, JPEG, PNG, HEIC, HEIF, WebP, TIF, TIFF

**Videos:** MP4, MOV, AVI, MKV, M4V, 3GP

`--include` and `--exclude` filter this supported set; they do not enable arbitrary formats.

## Safety

- Copying is the default; moving requires `--move`.
- `--dry-run` performs no file or log writes.
- Destinations are never overwritten. Collisions receive `_001`, `_002`, and so on.
- The resolved output tree is excluded from scans, including recursive scans.
- Per-file I/O errors are reported and processing continues.
- The command exits non-zero if any file failed.

## Troubleshooting

- **No files scanned:** add `--recursive` for nested files and check extension filters.
- **A file reports missing metadata:** `--timestamp exif` forbids filesystem fallback; use
  `--timestamp auto` or `--timestamp filesystem`.
- **Video dates are not found:** install MediaInfo and retry; `auto` still falls back to mtime.
- **Wrong wall-clock time:** pass an IANA zone such as `--timezone Europe/London`.
- **Unexpected duplicate suffix:** the unsuffixed destination already exists or another file in
  the same run reserved it. This is intentional overwrite protection.

See the [troubleshooting guide](docs/troubleshooting.md) for more detail.

## FAQ

**Does it change metadata?**

No. It copies or moves files and changes destination names only.

**Does it find duplicate photos?**

No. Collision handling prevents overwrites but is not content-based duplicate detection.

**Can I undo a move?**

There is no undo command in v1. Use copy mode and `--dry-run`; `--log-file` creates an
undo-friendly audit trail.

**What does `--preserve-source` preserve?**

It preserves the detected source label in the filename and is equivalent to `--format source`.
It does not mean “keep originals”; originals are already preserved by default copy mode.

**Where are unknown sources placed?**

They use the `Unknown` label when source naming or organisation is enabled.

## Documentation and development

The full guide is in [`docs/`](docs/index.md). Build it locally with:

```bash
mkdocs serve
```

Run the project checks with:

```bash
pytest
ruff check .
mypy src
mkdocs build --strict
```

This project is released under the MIT License; see [`LICENCE`](LICENCE).
