<p align="center">
    <a href="https://github.com/lupaxa-miscellaneous-toolbox">
        <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/miscellaneous-toolbox/readme-logo.png" alt="Organisation Logo" />
    </a>
</p>

<h1 align="center">Photo Renamer</h1>

`lupaxa-photo-renamer` safely copies or moves photographs and videos into
consistent, date-based filenames. The console command is `photo-renamer`.

It reads image EXIF or video metadata when available, falls back to filesystem
modification time in the default mode, detects common source apps from
filenames, and reports progress with [Rich](https://github.com/Textualize/rich).

## Installation

Python 3.13 or newer is required.

```bash
pip install lupaxa-photo-renamer
```

Using a virtual environment is recommended:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install lupaxa-photo-renamer
```

For local development:

```bash
git clone https://github.com/lupaxa-miscellaneous-toolbox/photo-renamer.git
cd photo-renamer
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Video timestamp extraction uses MediaInfo. If it is missing, install it with
your operating system's package manager (`brew install mediainfo` on macOS,
`apt install mediainfo` on Debian/Ubuntu). `auto` still falls back to
filesystem modification time.

## Quick Start

`PATH` is the directory to scan. Preview the work first:

```bash
photo-renamer --dry-run --recursive ~/Pictures
```

Review the startup panel (root, output, operation, format, timestamp mode, file
count). Then run the same command without `--dry-run`:

```bash
photo-renamer --recursive ~/Pictures
```

By default, files are **copied**, originals remain untouched, and results are
written below `PATH/renamed/`. Only files directly inside `PATH` are scanned
unless you add `--recursive`. Existing relative directories are preserved:

```text
Pictures/holiday/day-1/IMG-20260801-WA0001.JPG
→ Pictures/renamed/holiday/day-1/2026-08-01_14-55-22.jpg
```

Use `--move` only when you intentionally want to remove each successfully
processed source.

## Common Examples

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

# Limit extensions and always use modification time
photo-renamer --recursive --include jpg,jpeg,heic --timestamp filesystem ~/Pictures
```

A relative `--output` resolves below `PATH`. `--verbose` and `--quiet` cannot
be used together.

## Flag Summary

| Flag                                      | Purpose                                             |
| :---------------------------------------- | :-------------------------------------------------- |
| `--output DIR`                            | Output root; defaults to `renamed` under `PATH`     |
| `--recursive`                             | Scan subdirectories; off by default                 |
| `--dry-run`                               | Plan and report without writing                     |
| `--move`                                  | Move files instead of copying                       |
| `--timestamp auto\|exif\|filesystem`      | Select the timestamp strategy                       |
| `--format datetime\|source\|source-first` | Select the filename format                          |
| `--preserve-source`                       | Alias for `--format source`                         |
| `--organise`                              | Nest the detected source inside the relative path   |
| `--flatten`                               | Remove relative path segments from destinations     |
| `--include EXT,...`                       | Process only listed supported extensions            |
| `--exclude EXT,...`                       | Exclude listed extensions                           |
| `--skip-existing`                         | Skip files already matching a target naming pattern |
| `--force`                                 | Process matching names even with `--skip-existing`  |
| `--timezone ZONE`                         | Convert timestamps to an IANA zone before naming    |
| `--log-file PATH`                         | Append a tab-separated audit log on real runs       |
| `--workers N`                             | Concurrent copy/move workers (default `1`)          |
| `--yes` / `-y`                            | Assume yes for over-cap workers confirmation        |
| `--verbose` / `--quiet`                   | Increase or suppress terminal output                |

If both `--format` and `--preserve-source` are supplied, the explicit
`--format` value wins.

`--workers` only parallelises copy or move. Planning stays sequential so
collision-safe names stay stable. If `--workers` is greater than twice the
detected CPU count, photo-renamer asks for confirmation (use `--yes` in CI).

`--log-file` is not written during `--dry-run`. Each line is
`timestamp`, `action`, `source`, `destination`, `source label`,
`timestamp origin`, and `message`.

Run `photo-renamer --help` for the authoritative command syntax.

## Filename Formats

| Format         | Example                            |
| :------------- | :--------------------------------- |
| `datetime`     | `2026-08-01_14-55-22.jpg`          |
| `source`       | `2026-08-01_14-55-22_WhatsApp.jpg` |
| `source-first` | `WhatsApp_2026-08-01_14-55-22.jpg` |

Extensions are preserved and lowercased. `datetime` is the default.

For `PATH/vacation/day-1/IMG-20260801-WA0001.jpg`:

| Options                | Destination below output                          |
| :--------------------- | :------------------------------------------------ |
| none                   | `vacation/day-1/2026-08-01_14-55-22.jpg`          |
| `--organise`           | `vacation/day-1/WhatsApp/2026-08-01_14-55-22.jpg` |
| `--flatten`            | `2026-08-01_14-55-22.jpg`                         |
| `--flatten --organise` | `WhatsApp/2026-08-01_14-55-22.jpg`                |

`--organise` nests the detected source **inside** the preserved relative path.

## Supported Formats

| Kind   | Extensions                                  |
| :----- | :------------------------------------------ |
| Images | JPG, JPEG, PNG, HEIC, HEIF, WebP, TIF, TIFF |
| Videos | MP4, MOV, AVI, MKV, M4V, 3GP                |

Matching is case-insensitive. `--include` and `--exclude` filter this supported
set; they do not enable arbitrary formats.

## Timestamps

Every output name uses a resolved timestamp as `YYYY-MM-DD_HH-MM-SS`.

| Mode         | Behaviour                                                       |
| :----------- | :-------------------------------------------------------------- |
| `auto`       | Embedded metadata when available, otherwise filesystem mtime    |
| `exif`       | Embedded only (EXIF or MediaInfo); missing dates fail that file |
| `filesystem` | Always use filesystem mtime                                     |

Image priority: EXIF `DateTimeOriginal`, then `DateTimeDigitized`, then
`DateTime`, then filesystem mtime when the mode allows fallback.

Video priority: MediaInfo recorded, creation, encoded, then tagged dates,
then filesystem mtime.

`--timezone ZONE` accepts IANA identifiers such as `Europe/London`. The tool
reads metadata only; it never rewrites EXIF or video tags.

## Source Detection

Rules are case-insensitive; the first match wins. Detection uses the original
filename only — not pixels or maker tags.

| Label      | Patterns                                                         |
| :--------- | :--------------------------------------------------------------- |
| WhatsApp   | `IMG-…-WA…`, `VID-…-WA…`                                         |
| Telegram   | `Photo_…`, `Video_…`                                             |
| Signal     | `signal-…`, or a name ending with `_signal` before its extension |
| Pixel      | `PXL_…`                                                          |
| Samsung    | eight digits then `_` (for example `20260801_…`)                 |
| iPhone     | `IMG_` followed by four digits                                   |
| Screenshot | `Screenshot…`, `Screen Shot…`, `Screen_…`                        |
| Camera     | `DSC_…`, `DSCF…`                                                 |
| Unknown    | anything else                                                    |

## Safety

| Guarantee           | Behaviour                                                   |
| :------------------ | :---------------------------------------------------------- |
| Copy by default     | Moving requires `--move`                                    |
| Dry run             | `--dry-run` performs no file or log writes                  |
| Never overwrite     | Collisions receive `_001`, `_002`, and so on                |
| Output excluded     | The resolved output tree is never scanned                   |
| Continue on errors  | Per-file I/O errors are reported; later files still process |
| Non-zero on failure | The command exits non-zero if any file failed               |

Unreadable subdirectories are skipped without aborting the run. A mistyped
`PATH` is a configuration error.

## Exit Codes

| Code | Meaning                                                                |
| :--- | :--------------------------------------------------------------------- |
| `0`  | Every scanned file succeeded or was intentionally skipped              |
| `1`  | At least one file failed (including missing metadata in `exif` mode)   |
| `2`  | Invalid configuration (unknown timezone, quiet+verbose, bad `PATH`, …) |

## Troubleshooting

| Symptom                  | What to try                                                 |
| :----------------------- | :---------------------------------------------------------- |
| No files scanned         | Add `--recursive`; check `--include` / `--exclude`          |
| Missing metadata         | Use `--timestamp auto` or `--timestamp filesystem`          |
| Video dates not found    | Install MediaInfo; `auto` still falls back to mtime         |
| Wrong wall-clock time    | Pass an IANA zone such as `--timezone Europe/London`        |
| Unexpected `_001` suffix | Destination already existed or was reserved in the same run |

Files inside the resolved output directory are ignored. Symlinks are not
followed. `--timestamp exif` fails any file that has no embedded date.

## FAQ

| Question                                | Answer                                                               |
| :-------------------------------------- | :------------------------------------------------------------------- |
| Does it change metadata?                | No. It copies or moves files and changes destination names only.     |
| Does it find duplicate photos?          | No. Collisions prevent overwrites; they are not content hashes.      |
| Can I undo a move?                      | Not in v1. Prefer copy mode, `--dry-run`, and `--log-file`.          |
| What does `--preserve-source` preserve? | The source label in the filename (`--format source`), not originals. |
| Where do unknown sources go?            | They use the `Unknown` label when naming or organising by source.    |
| Can it overwrite a file?                | No. Unique suffixes and exclusive destination creation prevent it.   |

## Testing

```bash
make init
make python-install-dev
make python-check
```

Or without Make:

```bash
python -m pip install -e ".[test]"
pytest
```

Coverage for `lupaxa.photo_renamer` is reported by default.

This project is released under the MIT License; see [`LICENCE`](LICENCE).

<a href="https://github.com/the-lupaxa-project">
  <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
