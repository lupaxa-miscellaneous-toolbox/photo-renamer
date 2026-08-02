# Installation

## Requirements

- Python 3.13 or newer
- MediaInfo for extracting embedded timestamps from videos

Install MediaInfo using your operating system's package manager. The exact package name varies;
common names include `mediainfo` and `MediaInfo`.

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
git clone https://github.com/lupaxa-code-playground/photo-renamer.git
cd photo-renamer
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

For tests, type checking, linting, and documentation:

```bash
python -m pip install -e ".[dev]"
```

## Verify the installation

```bash
photo-renamer --dry-run /path/to/photos
```

The command should print a Rich startup panel and summary without creating files.
