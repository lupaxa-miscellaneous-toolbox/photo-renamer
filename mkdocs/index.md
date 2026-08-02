# Photo Renamer

`lupaxa-photo-renamer` is a Python CLI for safely copying or moving photographs and
videos into consistent, date-based filenames.

The PyPI package is **`lupaxa-photo-renamer`**. The console command is
**`photo-renamer`**.

## What it does

- Reads image EXIF and video MediaInfo creation times
- Falls back to filesystem modification time when needed
- Detects common source apps and devices from filenames
- Preserves relative directories or flattens output
- Optionally groups files by detected source
- Never overwrites destinations (uses `_001`, `_002`, … suffixes)
- Shows startup, progress, and summary output with Rich

## Safe defaults

- Files are **copied**, not moved
- Output goes to `PATH/renamed/`
- Relative directory structure is preserved
- Naming format is `YYYY-MM-DD_HH-MM-SS.ext`
- The resolved output tree is never scanned again

## Next steps

- [Getting started](getting-started.md) — install and first run
- [Usage](usage.md) — common workflows and troubleshooting
- [Reference](reference.md) — commands, metadata, and source rules
- [Examples](examples.md) — copy-paste recipes
