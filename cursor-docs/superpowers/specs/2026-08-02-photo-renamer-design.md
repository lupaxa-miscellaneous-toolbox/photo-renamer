# Photo Renamer — Design

**Date:** 2026-08-02  
**Status:** Approved for planning  
**Scope:** Greenfield Python CLI to rename/copy photographs and videos into consistent date-based filenames, with optional source labelling and folder organisation. Production-quality package suitable for open-source release.

## Goal

Ship **`lupaxa-photo-renamer`**: a typed, well-tested CLI (`photo-renamer`) that derives capture timestamps from metadata (with filesystem fallback), detects common source apps from filenames, writes safely under an output directory (never overwriting), and reports progress with Rich.

## Non-goals (v1)

- OCR / face recognition / perceptual hashing / duplicate detection
- Undo / reverse-rename CLI (log format must remain undo-friendly)
- EXIF editing, GPS folders, albums, watch mode, GUI
- User config files, custom filename templates, plugin entry points
- Parallel metadata extraction

## Packaging (align with favicon-generator)

| Concern | Value |
|---------|--------|
| Dist name | `lupaxa-photo-renamer` |
| Import path | `lupaxa.photo_renamer` |
| Layout | `src/lupaxa/photo_renamer/` |
| Console script | `photo-renamer` → `lupaxa.photo_renamer.cli:main` |
| Build | Hatchling |
| Author | The Lupaxa Project |
| License file | `LICENCE` (MIT) |
| Python | `>=3.13` |
| Version | `src/lupaxa/photo_renamer/version.py` + bump-my-version |
| Docs for PyPI | `README.md` + `README-PYPI.md` as needed |

### Dependencies

**Runtime:** rich, pillow, pillow-heif, platformdirs, pymediainfo  

**Dev:** pytest, pytest-cov, ruff, mypy, bump-my-version (and related tooling mirrored from favicon-generator where useful)

## Architecture

Pipeline of pure modules (Approach 1). CLI parses flags into validated config; scanner yields media paths lazily; each file runs through metadata → source detection → filename build → destination resolve → collision unique → copy/move (unless dry-run); reporting aggregates stats and optional log.

```text
PATH + CLI flags
    → config.AppConfig
    → scanner.iter_media_files (lazy; skip output tree)
    → per file:
          metadata.extract_timestamp
          source_detection.detect_source
          rename.build_filename
          organiser.resolve_destination
          collisions.ensure_unique
          execute copy|move (unless dry-run)
    → reporting + optional --log-file
```

### Core types (frozen dataclasses)

- `MediaFile` — path, extension, size
- `TimestampResult` — datetime, origin (`exif` / `mediainfo` / `filesystem` / `none`), missing flag
- `RenamePlan` — source path, dest path, detected source, timestamp info, action (`copy` / `move` / `skip`)
- `RunStats` — scanned, renamed (copied/moved), skipped, failed, collisions, metadata_missing

### Package layout

```text
photo-renamer/
├── pyproject.toml
├── README.md
├── README-PYPI.md
├── LICENCE
├── src/lupaxa/photo_renamer/
│   ├── __init__.py
│   ├── version.py
│   ├── cli.py
│   ├── config.py
│   ├── constants.py
│   ├── scanner.py
│   ├── metadata.py
│   ├── source_detection.py
│   ├── rename.py
│   ├── collisions.py
│   ├── organiser.py
│   ├── progress.py
│   ├── reporting.py
│   ├── utils.py
│   └── exceptions.py
├── tests/
├── docs/                    # MkDocs content
└── cursor-docs/superpowers/ # design & plans
```

Future features (plugins, OCR detectors, undo) plug in at module boundaries without a plugin framework in v1.

## CLI & behaviour

**Invocation:** `photo-renamer [options] PATH`

### Defaults

| Setting | Default |
|---------|---------|
| Output | `--output renamed` (under `PATH` if relative) |
| Transfer | **Copy** (preserve originals) |
| Structure | Preserve relative paths under output |
| Timestamp mode | `auto` |
| Naming format | `datetime` |
| Recursion | Off unless `--recursive` |

The resolved output directory is **never scanned**, even under `--recursive`, to avoid reprocessing.

### Flags

| Flag | Behaviour |
|------|-----------|
| `--recursive` | Search subdirectories |
| `--dry-run` | Plan only; no writes |
| `--verbose` / `--quiet` | Output verbosity |
| `--force` | Process even if already looks correctly named |
| `--skip-existing` | Skip files already matching target naming pattern |
| `--timestamp auto\|exif\|filesystem` | Timestamp strategy |
| `--format datetime\|source\|source-first` | Sole naming control |
| `--preserve-source` | Alias for `--format source` |
| `--organise` | Nest source label inside relative path |
| `--flatten` | Drop relative path segments |
| `--move` | Relocate instead of copy |
| `--output DIR` | Destination root (default `renamed`) |
| `--include` / `--exclude` | Extension filters |
| `--timezone` | Convert timestamp before naming |
| `--log-file PATH` | Event log for auditing / future undo |

### Destination resolution

Relative to `PATH` (examples use file `vacation/day1/IMG-…-WA….jpg`):

| Mode | Destination |
|------|-------------|
| Default | `PATH/renamed/vacation/day1/2026-08-01_13-45-22.jpg` |
| `--organise` | `PATH/renamed/vacation/day1/WhatsApp/2026-08-01_13-45-22.jpg` |
| `--flatten` | `PATH/renamed/2026-08-01_13-45-22.jpg` |
| `--flatten --organise` | `PATH/renamed/WhatsApp/2026-08-01_13-45-22.jpg` |

`--organise` places the source folder **inside** the preserved relative path (not as an outer prefix).

### Safety

- Never overwrite existing destinations
- Collisions: append `_001`, `_002`, … before the extension
- Per-file errors do not abort the run
- Exit code non-zero if any file failed; zero if all succeeded or were skipped

## Metadata

### Images (Pillow + pillow-heif)

Priority: EXIF DateTimeOriginal → DateTimeDigitized → DateTime → filesystem mtime.

Prefer EXIF-only reads; do not decode full pixel buffers for naming.

### Videos (pymediainfo)

MediaInfo creation/encoded date → filesystem mtime. Corrupt or unreadable media: fall back or fail that file gracefully and continue.

### `--timestamp` modes

- `auto` — metadata when available, else filesystem
- `exif` — embedded metadata only (image EXIF or video MediaInfo); if missing, fail/skip that file (no silent filesystem substitute). Flag name kept as `exif` for CLI familiarity; applies to both media types.
- `filesystem` — mtime only

### Timezone

If `--timezone` is set, convert the resolved datetime into that zone before formatting the filename. If unset, use the datetime as extracted (naive or aware per extractor behaviour; document in usage docs).

## Source detection

Pattern-based, first match wins. Ordered table in `source_detection.py` / `constants.py`:

| Source | Patterns (illustrative) |
|--------|-------------------------|
| WhatsApp | `IMG-*-WA*`, `VID-*-WA*` |
| Telegram | `Photo_*`, `Video_*` |
| Signal | `signal-*`, `Signal-*\.*`, `*_signal` (case-insensitive; extendable) |
| Pixel | `PXL_*` |
| Samsung | `YYYYMMDD_*` (e.g. `20260801_*`) |
| iPhone | `IMG_####` (and common variants as needed) |
| Screenshot | `Screenshot*`, `Screen Shot*`, `Screen_*` |
| Camera | `DSC_*`, `DSCF*` |
| Unknown | default |

Designed so additional detectors (including future OCR) can be added without changing the pipeline contract.

## Filename formats

Extension preserved and **lowercased**.

| Format | Pattern | Example |
|--------|---------|---------|
| `datetime` | `YYYY-MM-DD_HH-MM-SS.ext` | `2026-08-01_14-55-22.jpg` |
| `source` | `YYYY-MM-DD_HH-MM-SS_Source.ext` | `2026-08-01_14-55-22_WhatsApp.jpg` |
| `source-first` | `Source_YYYY-MM-DD_HH-MM-SS.ext` | `WhatsApp_2026-08-01_14-55-22.jpg` |

## Supported extensions

**Images:** jpg, jpeg, png, heic, heif, webp, tif, tiff  

**Videos:** mp4, mov, avi, mkv, m4v, 3gp  

`--include` / `--exclude` filter this set.

## Collisions

If `2026-08-01_14-55-22.jpg` exists, use `2026-08-01_14-55-22_001.jpg`, then `_002`, etc. Never overwrite. Count collisions in the summary.

## Output, errors & logging

### Rich UI

1. Startup summary: path, recursive, dry-run, copy/move, output, format, timestamp mode
2. Progress: phase 1 scans and collects matching paths (paths only); phase 2 processes with a determinate progress bar. Holding ~100k paths in memory is acceptable; do not load file contents during scan.
3. Summary table: scanned, copied/moved, skipped, failed, collisions, metadata missing
4. `--verbose` — per-file lines; `--quiet` — summary and errors only

### Error handling

Gracefully handle unreadable files, corrupt EXIF/video, permission errors, invalid filenames, path length issues. Continue processing; include failures in summary and log.

### Log file

`--log-file` records timestamped events: action, original path, new path, source label, timestamp origin, errors/skips. Format must be sufficient for a future reverse/undo feature.

### Performance

Target: comfortable at 100,000+ files via lazy scanning, one-file-at-a-time processing, and metadata-only reads (no unnecessary image decode).

## Testing

Unit tests for:

- Metadata extraction and fallbacks (including corrupt fixtures)
- Source detection patterns
- Filename generation (all formats + timezone)
- Collision suffixing
- Scanner (recursive, extension filters, skip output dir)
- Organiser path resolution (organise / flatten combinations)
- CLI parsing (including `--preserve-source` alias)
- Copy vs move vs dry-run against temporary directories

Quality gates: ruff, mypy (no warnings), pytest (+ coverage).

## Documentation

- **README:** installation, supported formats, examples, Rich screenshots, troubleshooting, FAQ
- **MkDocs:** installation, usage, command reference, examples, metadata behaviour, source detection, organising media, troubleshooting, development
- **LICENCE:** MIT text in file named `LICENCE` (not `LICENSE.md`)

## Future seams

Architecture leaves clear extension points without implementing them:

- Additional / OCR source detectors behind `detect_source`
- Hash-based duplicate detection as an optional pre-step
- Reverse rename from log / undo command
- Config file + custom templates feeding `build_filename`
- Plugin-registered detectors
- Parallel metadata workers behind the same per-file pipeline
- Optional GUI calling the same library API

## Acceptance criteria

- Builds cleanly; ruff and mypy pass; pytest suite passes
- Correctly processes images and videos per metadata rules
- Never overwrites; copy-by-default; `--move` optional
- Clear Rich output and optional log file
- Comprehensive README + MkDocs
- Packaged as `lupaxa-photo-renamer` suitable for publishing
)