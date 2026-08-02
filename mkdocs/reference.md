# Reference

```text
photo-renamer [options] PATH
```

`PATH` must be an existing directory to scan.

## Options

| Option              | Default       | Behaviour                                                         |
| :------------------ | :------------ | ----------------------------------------------------------------- |
| `--output DIR`      | `renamed`     | Destination root; relative paths resolve below `PATH`             |
| `--recursive`       | off           | Search subdirectories                                             |
| `--dry-run`         | off           | Plan and report without writing                                   |
| `--verbose`         | off           | Print per-file actions and failures                               |
| `--quiet`           | off           | Suppress startup, progress, summary, and verbose output           |
| `--force`           | off           | Process already named files when `--skip-existing` is also set    |
| `--skip-existing`   | off           | Skip files matching a generated date-based name                   |
| `--timestamp MODE`  | `auto`        | `auto`, `exif`, or `filesystem`                                   |
| `--format FORMAT`   | `datetime`    | `datetime`, `source`, or `source-first`                           |
| `--preserve-source` | off           | Alias for `--format source`; explicit `--format` wins             |
| `--organise`        | off           | Append detected source beneath the preserved relative directory   |
| `--flatten`         | off           | Remove relative source directories from output paths              |
| `--move`            | off           | Move instead of copy                                              |
| `--include EXT,...` | all supported | Include only listed supported extensions                          |
| `--exclude EXT,...` | none          | Exclude listed extensions                                         |
| `--timezone ZONE`   | unset         | Convert timestamps to an IANA zone before formatting              |
| `--log-file PATH`   | unset         | Append tab-separated audit events on real runs                    |

## Exit codes

| Code | Meaning                                                                 |
| ---- | ----------------------------------------------------------------------- |
| `0`  | Every scanned file succeeded or was intentionally skipped               |
| `1`  | At least one file failed (including missing metadata in `exif` mode)    |
| `2`  | Invalid configuration (unknown timezone, quiet+verbose, bad `PATH`, …)  |

## Safety guarantees

Copy is the default. Destinations are claimed exclusively and never overwritten.
Taken names become `_001`, `_002`, and so on. The resolved output tree is
excluded from scans. Unreadable subdirectories are skipped without aborting the
run; mistyped `PATH` values raise a configuration error (exit `2`).

## Filename formats

| Format          | Pattern                              | Example                            |
| --------------- | ------------------------------------ | ---------------------------------- |
| `datetime`      | `YYYY-MM-DD_HH-MM-SS.ext`            | `2026-08-01_14-55-22.jpg`          |
| `source`        | `YYYY-MM-DD_HH-MM-SS_Source.ext`     | `2026-08-01_14-55-22_WhatsApp.jpg` |
| `source-first`  | `Source_YYYY-MM-DD_HH-MM-SS.ext`     | `WhatsApp_2026-08-01_14-55-22.jpg` |

Extensions are preserved and lowercased.

## Metadata and timestamps

Every output filename uses a resolved timestamp as `YYYY-MM-DD_HH-MM-SS`.

### Image priority

1. EXIF `DateTimeOriginal`
2. EXIF `DateTimeDigitized`
3. EXIF `DateTime`
4. Filesystem modification time (when the mode allows fallback)

### Video priority

MediaInfo recorded/creation/encoded/tagged dates, then filesystem modification
time. Install the MediaInfo system package for embedded video timestamps.

### Timestamp modes

| Mode          | Behaviour                                                                 |
| :------------ | :------------------------------------------------------------------------ |
| `auto`        | Embedded metadata when available, otherwise filesystem mtime              |
| `exif`        | Embedded only (EXIF or MediaInfo); missing dates fail that file           |
| `filesystem`  | Always use filesystem mtime                                               |

`--timezone ZONE` accepts IANA identifiers such as `Europe/London`. The tool
reads metadata only; it never rewrites EXIF or video tags.

## Source detection

Rules are case-insensitive; the first match wins.

| Label       | Patterns                                                         |
| :---------- | :--------------------------------------------------------------- |
| WhatsApp    | `IMG-…-WA…`, `VID-…-WA…`                                         |
| Telegram    | `Photo_…`, `Video_…`                                             |
| Signal      | `signal-…`, or a name ending with `_signal` before its extension |
| Pixel       | `PXL_…`                                                          |
| Samsung     | eight digits then `_` (for example `20260801_…`)                 |
| iPhone      | `IMG_` followed by four digits                                   |
| Screenshot  | `Screenshot…`, `Screen Shot…`, `Screen_…`                        |
| Camera      | `DSC_…`, `DSCF…`                                                 |
| Unknown     | anything else                                                    |

Detection uses the original filename only — not pixels or maker tags.

## Architecture

```text
CLI configuration
  → scan supported media
  → extract timestamp
  → detect source
  → build filename
  → resolve organised destination
  → reserve collision-safe name
  → copy or move
  → report and optionally log
```

Package layout uses Hatchling under `src/lupaxa/photo_renamer/`. The console
entry point is `lupaxa.photo_renamer.cli:main`.
