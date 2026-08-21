<!-- markdownlint-disable -->
<p align="center">
  <a href="https://github.com/lupaxa-miscellaneous-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/miscellaneous-toolbox/readme-logo.png" alt="Project Logo" width="256"/><br/>
  </a>
</p>
<h3 align="center">
  The Lupaxa Miscellaneous Toolbox<br />
  Part of The Lupaxa Project
</h3>

<br />

# lupaxa-photo-renamer

Safely copy or move photographs and videos into consistent date-based
filenames. Reads image EXIF or video metadata when available, falls back to
filesystem modification time, detects common source apps, and reports progress
with Rich.

Built for media libraries used by The Lupaxa Project.

## Features

- Date-based filenames from EXIF, video metadata, or filesystem mtime
- Copy by default; `--move` only when you intend to remove sources
- `--dry-run` plans and reports without writing files or logs
- Never overwrites: collisions get `_001`, `_002`, and so on
- Optional source labels in names (`datetime`, `source`, `source-first`)
- Optional organise / flatten layout for detected sources
- Concurrent copy/move workers and a tab-separated audit log
- Fully typed, linted, formatted, and tested
- MkDocs documentation included

## Installation

### From PyPI

```bash
pip install lupaxa-photo-renamer
```

### From source (development mode)

```bash
pip install -e ".[dev]"
```

The console command is `photo-renamer`.

Video timestamp extraction uses MediaInfo. If it is unavailable on your
system, install the MediaInfo package with your operating system's package
manager (`brew install mediainfo` on macOS or `apt install mediainfo` on
Debian/Ubuntu). `auto` still falls back to filesystem mtime.

## CLI quick start

```bash
photo-renamer --help
photo-renamer --dry-run --recursive ~/Pictures
photo-renamer --recursive ~/Pictures
photo-renamer --recursive --format source ~/Pictures
photo-renamer --recursive --organise ~/Pictures
photo-renamer --recursive --output /Volumes/Archive --move ~/Pictures
```

By default, files are copied and results are written below `PATH/renamed/`.
Existing relative directories are preserved:

```text
Pictures/holiday/day-1/IMG-20260801-WA0001.JPG
→ Pictures/renamed/holiday/day-1/2026-08-01_14-55-22.jpg
```

## Requirements

- Python 3.13+
- Runtime dependencies: `rich`, `Pillow`, `pillow-heif`, `platformdirs`,
  `pymediainfo`
- System MediaInfo for video timestamps (optional; mtime fallback remains)

## Documentation

Online documentation:

[Documentation](https://photo-renamer.thelupaxaproject.org/)

Source repository:

[GitHub](https://github.com/lupaxa-miscellaneous-toolbox/photo-renamer)

### Serve docs locally

From a clone of the repository:

```bash
make mkdocs-serve
```

Then open the local URL printed by MkDocs in your browser.

## Development

Clone the repository and install with Make:

```bash
make init                # first-time makefile-skills checkout
make python-install-dev  # editable install with [dev]
make python-check        # lint, type-check, and test
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
