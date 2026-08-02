<p align="center">
    <a href="https://github.com/code-playground">
        <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/code-playground/readme-logo.png" alt="Organisation Logo" />
    </a>
</p>

<h1 align="center">Photo Renamer</h1>

`lupaxa-photo-renamer` safely copies or moves photographs and videos into
consistent, date-based filenames. It reads image EXIF or video metadata when
available, falls back to filesystem modification time in the default mode,
detects common source apps, and reports progress with
[Rich](https://github.com/Textualize/rich).

> A Rich terminal screenshot will be added under `mkdocs/assets/`. Until then,
> the startup panel, progress bar, and summary table are shown directly in your
> terminal.

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

Video timestamp extraction uses MediaInfo. If it is unavailable on your system,
install the MediaInfo package with your operating system's package manager.

## Quick start

Preview the work first:

```bash
photo-renamer --dry-run --recursive ~/Pictures
```

Then run the same command without `--dry-run`:

```bash
photo-renamer --recursive ~/Pictures
```

By default, files are **copied**, originals remain untouched, and results are
written below `PATH/renamed/`. Existing relative directories are preserved:

```text
Pictures/holiday/day-1/IMG-20260801-WA0001.JPG
→ Pictures/renamed/holiday/day-1/2026-08-01_14-55-22.jpg
```

Use `--move` only when you intentionally want to remove each successfully
processed source.

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
| `--log-file PATH`                         | Append a tab-separated audit log                    |
| `--workers N`                             | Concurrent copy/move workers (default `1`)          |
| `--yes` / `-y`                            | Assume yes for over-cap workers confirmation        |
| `--verbose` / `--quiet`                   | Increase or suppress terminal output                |

Run `photo-renamer --help` for the authoritative command syntax.

## Filename formats

| Format         | Example                            |
| :------------- | :--------------------------------- |
| `datetime`     | `2026-08-01_14-55-22.jpg`          |
| `source`       | `2026-08-01_14-55-22_WhatsApp.jpg` |
| `source-first` | `WhatsApp_2026-08-01_14-55-22.jpg` |

Extensions are preserved and lowercased. `datetime` is the default.

## Supported formats

| Kind   | Extensions                                  |
| :----- | :------------------------------------------ |
| Images | JPG, JPEG, PNG, HEIC, HEIF, WebP, TIF, TIFF |
| Videos | MP4, MOV, AVI, MKV, M4V, 3GP                |

`--include` and `--exclude` filter this supported set; they do not enable
arbitrary formats.

## Safety

| Guarantee           | Behaviour                                                   |
| :------------------ | :---------------------------------------------------------- |
| Copy by default     | Moving requires `--move`                                    |
| Dry run             | `--dry-run` performs no file or log writes                  |
| Never overwrite     | Collisions receive `_001`, `_002`, and so on                |
| Output excluded     | The resolved output tree is never scanned                   |
| Continue on errors  | Per-file I/O errors are reported; later files still process |
| Non-zero on failure | The command exits non-zero if any file failed               |

## Troubleshooting

| Symptom                  | What to try                                                 |
| :----------------------- | :---------------------------------------------------------- |
| No files scanned         | Add `--recursive`; check `--include` / `--exclude`          |
| Missing metadata         | Use `--timestamp auto` or `--timestamp filesystem`          |
| Video dates not found    | Install MediaInfo; `auto` still falls back to mtime         |
| Wrong wall-clock time    | Pass an IANA zone such as `--timezone Europe/London`        |
| Unexpected `_001` suffix | Destination already existed or was reserved in the same run |

See the [usage guide](mkdocs/usage.md#troubleshooting) for more detail.

## FAQ

| Question                                | Answer                                                               |
| :-------------------------------------- | :------------------------------------------------------------------- |
| Does it change metadata?                | No. It copies or moves files and changes destination names only.     |
| Does it find duplicate photos?          | No. Collisions prevent overwrites; they are not content hashes.      |
| Can I undo a move?                      | Not in v1. Prefer copy mode, `--dry-run`, and `--log-file`.          |
| What does `--preserve-source` preserve? | The source label in the filename (`--format source`), not originals. |
| Where do unknown sources go?            | They use the `Unknown` label when naming or organising by source.    |

## Documentation and development

The full guide is in [`mkdocs/`](mkdocs/index.md), built with the Lupaxa
technical documentation template (Material theme under `overrides/`).

This repo uses [makefile-skills](https://github.com/the-lupaxa-blueprints/makefile-skills)
(`python` + `mkdocs`). First-time setup clones skills into `.makefiles/`
(gitignored):

```bash
make init
make install-dev
```

Common targets:

```bash
make python-check    # ruff + mypy + pytest
make mkdocs-serve    # live docs at http://127.0.0.1:8000
make mkdocs-build    # strict MkDocs build
make help
```

This project is released under the MIT License; see [`LICENCE`](LICENCE).

<a href="https://github.com/the-lupaxa-project">
  <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
