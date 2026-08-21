# Getting started

## Requirements

-   Python 3.13 or newer
-   MediaInfo for embedded video timestamps (`brew install mediainfo` on
    macOS, or `apt install mediainfo` on Debian/Ubuntu). `auto` still falls
    back to filesystem mtime if MediaInfo is missing.

## Install from PyPI

```bash
python -m pip install lupaxa-photo-renamer
photo-renamer --help
```

Using a virtual environment is recommended:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install lupaxa-photo-renamer
```

On Windows, activate with `.venv\Scripts\activate`.

## Install from a checkout

```bash
git clone https://github.com/lupaxa-miscellaneous-toolbox/photo-renamer.git
cd photo-renamer
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

This repo uses [makefile-skills](https://github.com/lupaxa-developers-toolbox/makefile-skills)
(`python` + `mkdocs`). First-time setup clones skills into `.makefiles/`
(gitignored):

```bash
make init
make python-install-dev
```

## First run

Always preview first:

```bash
photo-renamer --dry-run --recursive ~/Pictures
```

The command prints a Rich startup panel and summary without creating files. When
the plan looks correct, drop `--dry-run`:

```bash
photo-renamer --recursive ~/Pictures
```

Results land under `~/Pictures/renamed/` and originals stay in place.

## Supported formats

| Kind   | Extensions                                                  |
| :----- | :---------------------------------------------------------- |
| Images | `jpg`, `jpeg`, `png`, `heic`, `heif`, `webp`, `tif`, `tiff` |
| Videos | `mp4`, `mov`, `avi`, `mkv`, `m4v`, `3gp`                    |

Matching is case-insensitive. `--include` and `--exclude` filter this supported
set; they do not enable arbitrary formats.

## Development checks

```bash
make python-check    # ruff + mypy + pytest
make mkdocs-serve    # live local docs
make mkdocs-build    # strict MkDocs build
```

Documentation source lives in `mkdocs/` (`docs_dir: mkdocs` in `mkdocs.yml`),
not `docs/`, so GitHub’s special `/docs` path is unused.
