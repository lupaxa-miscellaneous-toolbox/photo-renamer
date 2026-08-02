# Photo Renamer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build installable `lupaxa-photo-renamer` (`photo-renamer` CLI) that copies/moves photos and videos into date-based names under an output tree with Rich progress, safe collisions, and full tests/docs.

**Architecture:** Pipeline of pure typed modules: CLI → `AppConfig` → scan paths → per-file metadata/source/name/destination/collision → copy or move → Rich report + optional log. Packaging mirrors `lupaxa-favicon-generator` (Hatchling, `src/lupaxa/...`).

**Tech Stack:** Python ≥3.13, rich, Pillow, pillow-heif, platformdirs, pymediainfo, pytest, pytest-cov, ruff, mypy, Hatchling, MkDocs

**Spec:** `cursor-docs/superpowers/specs/2026-08-02-photo-renamer-design.md`

## Global Constraints

- Dist name: `lupaxa-photo-renamer`; import: `lupaxa.photo_renamer`; script: `photo-renamer`
- License file must be named `LICENCE` (MIT), not `LICENSE.md`
- Python `>=3.13`; fully typed; ruff and mypy clean; pytest with coverage
- Copy by default; `--move` relocates; never overwrite destinations
- Default `--output` is `renamed` under `PATH`; never scan the resolved output tree
- `--format` owns naming; `--preserve-source` aliases `--format source`
- `--organise` nests source **inside** relative path; `--flatten` drops relative segments
- Specs/plans live under `cursor-docs/superpowers/` (never `docs/superpowers/`)
- Do not implement undo, plugins, watch mode, OCR, hashing, or GUI in this plan

## File structure

| File | Responsibility |
|------|----------------|
| `pyproject.toml` | Hatch package metadata, deps, scripts, ruff/mypy/pytest |
| `LICENCE` | MIT license text |
| `README.md` | User-facing install, examples, FAQ |
| `README-PYPI.md` | Short PyPI description |
| `.gitignore` | venvs, caches, build, `site/`, coverage |
| `src/lupaxa/photo_renamer/__init__.py` | Public exports + version |
| `src/lupaxa/photo_renamer/version.py` | `__version__`, `get_version()` |
| `src/lupaxa/photo_renamer/exceptions.py` | Error hierarchy |
| `src/lupaxa/photo_renamer/constants.py` | Extensions, EXIF tags, source labels |
| `src/lupaxa/photo_renamer/models.py` | Frozen dataclasses shared across modules |
| `src/lupaxa/photo_renamer/utils.py` | Path helpers, extension normalize, platformdirs log dir |
| `src/lupaxa/photo_renamer/source_detection.py` | Pattern → source label |
| `src/lupaxa/photo_renamer/collisions.py` | Unique destination paths |
| `src/lupaxa/photo_renamer/rename.py` | Filename build + apply copy/move |
| `src/lupaxa/photo_renamer/organiser.py` | Destination directory resolution |
| `src/lupaxa/photo_renamer/scanner.py` | Collect media paths |
| `src/lupaxa/photo_renamer/metadata.py` | Timestamp extraction |
| `src/lupaxa/photo_renamer/config.py` | `AppConfig` + argparse → config |
| `src/lupaxa/photo_renamer/progress.py` | Rich progress helpers |
| `src/lupaxa/photo_renamer/reporting.py` | Startup panel, summary table, log file |
| `src/lupaxa/photo_renamer/pipeline.py` | End-to-end run over scanned files |
| `src/lupaxa/photo_renamer/cli.py` | `main()` entry |
| `tests/` | Unit and CLI tests |
| `mkdocs/` + `mkdocs.yml` | MkDocs site (`docs_dir: mkdocs`) |
| `requirements.txt` | Runtime deps mirror |

Note: `models.py` and `pipeline.py` are intentional additions beyond the original sketch so shared types and orchestration stay testable without bloating `cli.py`.

---

### Task 1: Package scaffold and version

**Files:**
- Create: `pyproject.toml`, `LICENCE`, `.gitignore`, `requirements.txt`, `src/lupaxa/__init__.py`, `src/lupaxa/photo_renamer/__init__.py`, `src/lupaxa/photo_renamer/version.py`, `src/lupaxa/photo_renamer/exceptions.py`, `tests/test_version.py`

**Interfaces:**
- Consumes: nothing
- Produces: `get_version() -> str`, `PhotoRenamerError`, installable package name `lupaxa-photo-renamer`, script entry `photo-renamer = lupaxa.photo_renamer.cli:main` (cli stubbed later)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_version.py
from lupaxa.photo_renamer import version
from lupaxa.photo_renamer.version import get_version


def test_get_version_matches_dunder() -> None:
    assert get_version() == version.__version__
    assert get_version() == "0.1.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_version.py -v`  
Expected: FAIL (package / module not found)

- [ ] **Step 3: Create scaffold files**

`src/lupaxa/__init__.py` — empty or namespace docstring.

`src/lupaxa/photo_renamer/version.py`:

```python
"""Version information for lupaxa.photo_renamer."""

from __future__ import annotations

__version__ = "0.1.0"


def get_version() -> str:
    """Return the package version string."""
    return __version__
```

`src/lupaxa/photo_renamer/exceptions.py`:

```python
"""Exceptions for lupaxa.photo_renamer."""

from __future__ import annotations


class PhotoRenamerError(Exception):
    """Base error for photo-renamer."""


class ConfigError(PhotoRenamerError):
    """Invalid configuration or CLI arguments."""


class MetadataError(PhotoRenamerError):
    """Failed to read media metadata when required."""


class FileOperationError(PhotoRenamerError):
    """Copy/move/filesystem failure for a single file."""
```

`src/lupaxa/photo_renamer/__init__.py`:

```python
"""Lupaxa photo renamer package."""

from __future__ import annotations

from .exceptions import ConfigError, FileOperationError, MetadataError, PhotoRenamerError
from .version import get_version as version

__all__ = [
    "PhotoRenamerError",
    "ConfigError",
    "MetadataError",
    "FileOperationError",
    "version",
]
```

`LICENCE` — full MIT text, Copyright (c) 2026 The Lupaxa Project.

`.gitignore`:

```gitignore
__pycache__/
*.py[cod]
.venv/
venv/
dist/
build/
*.egg-info/
.mypy_cache/
.ruff_cache/
.pytest_cache/
.coverage
htmlcov/
site/
*.log
```

`requirements.txt`:

```text
rich>=13.0
Pillow>=10.0
pillow-heif>=0.16
platformdirs>=4.0
pymediainfo>=6.0
```

`pyproject.toml` (mirror favicon-generator; adapt names and Python 3.13):

```toml
[build-system]
requires = ["hatchling>=1.18"]
build-backend = "hatchling.build"

[project]
name = "lupaxa-photo-renamer"
version = "0.1.0"
description = "Rename photographs and videos into consistent date-based filenames."
readme = "README-PYPI.md"
license = { file = "LICENCE" }
requires-python = ">=3.13"

authors = [
  { name = "The Lupaxa Project" }
]

keywords = ["photos", "rename", "exif", "cli", "media"]

dependencies = [
  "rich>=13.0",
  "Pillow>=10.0",
  "pillow-heif>=0.16",
  "platformdirs>=4.0",
  "pymediainfo>=6.0",
]

classifiers = [
  "Development Status :: 4 - Beta",
  "Environment :: Console",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.13",
  "Topic :: Multimedia :: Graphics",
  "Topic :: Utilities",
]

[project.urls]
Homepage = "https://github.com/lupaxa-code-playground/photo-renamer"
Repository = "https://github.com/lupaxa-code-playground/photo-renamer"
Issues = "https://github.com/lupaxa-code-playground/photo-renamer/issues"

[project.scripts]
photo-renamer = "lupaxa.photo_renamer.cli:main"

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
  "pytest-cov>=5.0",
  "ruff>=0.6.0",
  "mypy>=1.12.0",
  "bump-my-version>=1.2.0",
  "pip-audit>=2.7.0",
  "mkdocs>=1.6.0",
  "mkdocs-material>=9.0",
]
test = [
  "pytest>=8.0",
  "pytest-cov>=5.0",
]

[tool.hatch.version]
path = "src/lupaxa/photo_renamer/version.py"

[tool.hatch.build.targets.wheel]
packages = ["src/lupaxa"]

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "S", "UP", "SIM", "C4", "ISC", "D", "ANN", "PT"]
ignore = [
  "D200", "D201", "D202", "D203", "D204", "D205", "D206", "D207", "D208", "D209", "D210", "D211", "D212",
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101", "S105", "D", "ANN001", "ANN201"]

[tool.ruff.lint.pydocstyle]
convention = "numpy"

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.13"
warn_unused_configs = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
follow_imports = "normal"
ignore_missing_imports = true

[tool.pytest.ini_options]
addopts = "-ra -q --disable-warnings --cov=lupaxa.photo_renamer --cov-report=term-missing"
testpaths = ["tests"]
pythonpath = ["src"]

[tool.coverage.run]
source = ["lupaxa.photo_renamer"]
branch = true

[tool.coverage.report]
show_missing = true
skip_empty = true
```

Create a minimal `README-PYPI.md`:

```markdown
# lupaxa-photo-renamer

Rename photographs and videos into consistent date-based filenames.

See the GitHub README for full documentation.
```

Stub `src/lupaxa/photo_renamer/cli.py` so the entry point exists:

```python
"""Command-line interface for lupaxa.photo_renamer."""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Fully implemented in a later task."""
    _ = argv
    print("photo-renamer: not implemented yet", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Install editable and run test**

Run:

```bash
python -m pip install -e ".[dev]"
python -m pytest tests/test_version.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml LICENCE .gitignore requirements.txt README-PYPI.md \
  src/lupaxa tests/test_version.py
git commit -m "$(cat <<'EOF'
Scaffold lupaxa-photo-renamer package layout and version.

EOF
)"
```

---

### Task 2: Shared models, constants, and utils

**Files:**
- Create: `src/lupaxa/photo_renamer/models.py`, `constants.py`, `utils.py`, `tests/test_utils.py`

**Interfaces:**
- Consumes: `exceptions` (none required)
- Produces:
  - `TimestampOrigin = Literal["exif", "mediainfo", "filesystem", "none"]`
  - `NameFormat = Literal["datetime", "source", "source-first"]`
  - `TimestampMode = Literal["auto", "exif", "filesystem"]`
  - `PlanAction = Literal["copy", "move", "skip"]`
  - `@dataclass(frozen=True) class MediaFile` — `path: Path`, `extension: str`, `size: int`
  - `@dataclass(frozen=True) class TimestampResult` — `value: datetime | None`, `origin: TimestampOrigin`, `missing: bool`
  - `@dataclass(frozen=True) class RenamePlan` — `source: Path`, `destination: Path`, `detected_source: str`, `timestamp: TimestampResult`, `action: PlanAction`, `skipped_reason: str | None`
  - `@dataclass class RunStats` — counters: `scanned`, `processed`, `skipped`, `failed`, `collisions`, `metadata_missing` (ints, mutable for aggregation)
  - `IMAGE_EXTENSIONS`, `VIDEO_EXTENSIONS`, `DEFAULT_EXTENSIONS`, `SOURCE_LABELS`
  - `normalize_extension(ext: str) -> str`
  - `is_supported_extension(ext: str, include: set[str] | None, exclude: set[str] | None) -> bool`
  - `user_log_dir() -> Path` via platformdirs

- [ ] **Step 1: Write failing tests**

```python
# tests/test_utils.py
from lupaxa.photo_renamer.utils import is_supported_extension, normalize_extension


def test_normalize_extension_strips_dot_and_lowercases() -> None:
    assert normalize_extension(".JPG") == "jpg"
    assert normalize_extension("HEIC") == "heic"


def test_is_supported_respects_include_exclude() -> None:
    assert is_supported_extension("jpg", include=None, exclude=None) is True
    assert is_supported_extension("gif", include=None, exclude=None) is False
    assert is_supported_extension("jpg", include={"png"}, exclude=None) is False
    assert is_supported_extension("jpg", include=None, exclude={"jpg"}) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_utils.py -v`  
Expected: FAIL (import error)

- [ ] **Step 3: Implement models, constants, utils**

Implement `constants.py` with:

```python
IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {"jpg", "jpeg", "png", "heic", "heif", "webp", "tif", "tiff"}
)
VIDEO_EXTENSIONS: frozenset[str] = frozenset(
    {"mp4", "mov", "avi", "mkv", "m4v", "3gp"}
)
DEFAULT_EXTENSIONS: frozenset[str] = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
```

Implement `models.py` with the frozen dataclasses listed in Interfaces.

Implement `utils.py`:

```python
def normalize_extension(ext: str) -> str:
    return ext.lower().lstrip(".")


def is_supported_extension(
    ext: str,
    include: set[str] | None,
    exclude: set[str] | None,
) -> bool:
    normalized = normalize_extension(ext)
    allowed = include if include is not None else set(DEFAULT_EXTENSIONS)
    allowed = {normalize_extension(e) for e in allowed}
    if normalized not in allowed:
        return False
    if exclude is not None and normalized in {normalize_extension(e) for e in exclude}:
        return False
    return True


def user_log_dir() -> Path:
    return Path(platformdirs.user_log_dir(appname="lupaxa-photo-renamer", appauthor="Lupaxa"))
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_utils.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/lupaxa/photo_renamer/models.py src/lupaxa/photo_renamer/constants.py \
  src/lupaxa/photo_renamer/utils.py tests/test_utils.py
git commit -m "$(cat <<'EOF'
Add shared models, media constants, and path helpers.

EOF
)"
```

---

### Task 3: Source detection

**Files:**
- Create: `src/lupaxa/photo_renamer/source_detection.py`, `tests/test_source_detection.py`

**Interfaces:**
- Consumes: none beyond stdlib `re` / `Path`
- Produces: `detect_source(filename: str) -> str` returning one of `WhatsApp`, `Telegram`, `Signal`, `Pixel`, `Samsung`, `iPhone`, `Screenshot`, `Camera`, `Unknown`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_source_detection.py
import pytest
from lupaxa.photo_renamer.source_detection import detect_source


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("IMG-20260801-WA0001.jpg", "WhatsApp"),
        ("VID-20260801-WA0002.mp4", "WhatsApp"),
        ("Photo_12345.jpg", "Telegram"),
        ("Video_12345.mp4", "Telegram"),
        ("signal-2026-08-01-123456.jpg", "Signal"),
        ("PXL_20260801_135522.jpg", "Pixel"),
        ("20260801_135522.jpg", "Samsung"),
        ("IMG_1234.JPG", "iPhone"),
        ("Screenshot 2026-08-01.png", "Screenshot"),
        ("Screen Shot 2026-08-01.png", "Screenshot"),
        ("Screen_001.png", "Screenshot"),
        ("DSC_0123.jpg", "Camera"),
        ("DSCF0001.JPG", "Camera"),
        ("holiday.jpg", "Unknown"),
    ],
)
def test_detect_source(name: str, expected: str) -> None:
    assert detect_source(name) == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_source_detection.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement detection**

Ordered first-match regex list (case-insensitive) in `source_detection.py`:

1. WhatsApp: `^IMG-.*-WA`, `^VID-.*-WA`
2. Telegram: `^Photo_`, `^Video_`
3. Signal: `^signal-`, `^Signal-`, `_signal(\.|$)`
4. Pixel: `^PXL_`
5. Samsung: `^\d{8}_`
6. iPhone: `^IMG_\d{4}`
7. Screenshot: `^Screenshot`, `^Screen Shot`, `^Screen_`
8. Camera: `^DSC_`, `^DSCF`
9. else `Unknown`

```python
def detect_source(filename: str) -> str:
    name = Path(filename).name
    for label, patterns in _RULES:
        for pattern in patterns:
            if pattern.search(name):
                return label
    return "Unknown"
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_source_detection.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/lupaxa/photo_renamer/source_detection.py tests/test_source_detection.py
git commit -m "$(cat <<'EOF'
Add pattern-based media source detection.

EOF
)"
```

---

### Task 4: Filename generation

**Files:**
- Create: `src/lupaxa/photo_renamer/rename.py` (build helpers only for now), `tests/test_rename.py`

**Interfaces:**
- Consumes: `NameFormat` from models; `detect_source` not required inside builder if source passed in
- Produces:
  - `format_timestamp(dt: datetime) -> str` → `YYYY-MM-DD_HH-MM-SS`
  - `build_filename(dt: datetime, extension: str, name_format: NameFormat, source: str) -> str`
  - `ALREADY_NAMED_RE` — regex matching `^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(_\d{3})?(_[A-Za-z]+)?$` stem patterns used by `--skip-existing` (datetime form and optional collision/source). Exact: stems matching `^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}` optionally followed by `_\d{3}` and/or `_[A-Za-z][A-Za-z0-9]*`, OR source-first `^[A-Za-z][A-Za-z0-9]*_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(_\d{3})?$`
  - `is_already_named(filename: str) -> bool`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_rename.py
from datetime import datetime
from lupaxa.photo_renamer.rename import build_filename, is_already_named


def test_build_filename_formats() -> None:
    dt = datetime(2026, 8, 1, 14, 55, 22)
    assert build_filename(dt, "JPG", "datetime", "WhatsApp") == "2026-08-01_14-55-22.jpg"
    assert build_filename(dt, "jpg", "source", "WhatsApp") == "2026-08-01_14-55-22_WhatsApp.jpg"
    assert (
        build_filename(dt, "jpg", "source-first", "WhatsApp")
        == "WhatsApp_2026-08-01_14-55-22.jpg"
    )


def test_is_already_named() -> None:
    assert is_already_named("2026-08-01_14-55-22.jpg") is True
    assert is_already_named("2026-08-01_14-55-22_001.jpg") is True
    assert is_already_named("2026-08-01_14-55-22_WhatsApp.jpg") is True
    assert is_already_named("WhatsApp_2026-08-01_14-55-22.jpg") is True
    assert is_already_named("IMG-20260801-WA0001.jpg") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_rename.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement builders in `rename.py`**

```python
def format_timestamp(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d_%H-%M-%S")


def build_filename(
    dt: datetime,
    extension: str,
    name_format: NameFormat,
    source: str,
) -> str:
    stamp = format_timestamp(dt)
    ext = normalize_extension(extension)
    if name_format == "datetime":
        stem = stamp
    elif name_format == "source":
        stem = f"{stamp}_{source}"
    elif name_format == "source-first":
        stem = f"{source}_{stamp}"
    else:
        msg = f"Unknown name format: {name_format}"
        raise ValueError(msg)
    return f"{stem}.{ext}"
```

Implement `is_already_named` with compiled regexes covering the three formats and `_NNN` collision suffix.

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_rename.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/lupaxa/photo_renamer/rename.py tests/test_rename.py
git commit -m "$(cat <<'EOF'
Add date-based filename builders and already-named detection.

EOF
)"
```

---

### Task 5: Collisions

**Files:**
- Create: `src/lupaxa/photo_renamer/collisions.py`, `tests/test_collisions.py`

**Interfaces:**
- Consumes: none
- Produces: `ensure_unique(destination: Path, *, reserved: set[Path] | None = None) -> tuple[Path, bool]`  
  Returns `(unique_path, collided)` where `collided` is True if a suffix was required. Checks filesystem existence and optional in-run `reserved` set. Suffixes `_001`, `_002`, … before extension.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_collisions.py
from pathlib import Path
from lupaxa.photo_renamer.collisions import ensure_unique


def test_ensure_unique_no_collision(tmp_path: Path) -> None:
    dest = tmp_path / "2026-08-01_14-55-22.jpg"
    path, collided = ensure_unique(dest)
    assert path == dest
    assert collided is False


def test_ensure_unique_suffixes(tmp_path: Path) -> None:
    existing = tmp_path / "2026-08-01_14-55-22.jpg"
    existing.write_bytes(b"x")
    path, collided = ensure_unique(existing)
    assert path == tmp_path / "2026-08-01_14-55-22_001.jpg"
    assert collided is True
    path.write_bytes(b"y")
    path2, _ = ensure_unique(existing)
    assert path2 == tmp_path / "2026-08-01_14-55-22_002.jpg"


def test_ensure_unique_respects_reserved(tmp_path: Path) -> None:
    dest = tmp_path / "2026-08-01_14-55-22.jpg"
    reserved = {dest.resolve()}
    path, collided = ensure_unique(dest, reserved=reserved)
    assert path == tmp_path / "2026-08-01_14-55-22_001.jpg"
    assert collided is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_collisions.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement `ensure_unique`**

```python
def ensure_unique(
    destination: Path,
    *,
    reserved: set[Path] | None = None,
) -> tuple[Path, bool]:
    reserved = reserved or set()

    def taken(path: Path) -> bool:
        return path.exists() or path.resolve() in reserved

    if not taken(destination):
        return destination, False
    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    n = 1
    while True:
        candidate = parent / f"{stem}_{n:03d}{suffix}"
        if not taken(candidate):
            return candidate, True
        n += 1
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_collisions.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/lupaxa/photo_renamer/collisions.py tests/test_collisions.py
git commit -m "$(cat <<'EOF'
Add collision-safe destination path allocation.

EOF
)"
```

---

### Task 6: Organiser destination resolution

**Files:**
- Create: `src/lupaxa/photo_renamer/organiser.py`, `tests/test_organiser.py`

**Interfaces:**
- Consumes: none
- Produces: `resolve_destination_dir(*, root: Path, output_dir: Path, source_file: Path, detected_source: str, organise: bool, flatten: bool) -> Path`  
  Semantics from spec:
  - relative parts = `source_file.relative_to(root).parent` (`.` if file is directly under root)
  - if `flatten`: ignore relative parts
  - if `organise`: append `detected_source` **after** relative parts
  - final dir = `output_dir / [relative parts...] / [source?]`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_organiser.py
from pathlib import Path
from lupaxa.photo_renamer.organiser import resolve_destination_dir


def test_preserve_relative(tmp_path: Path) -> None:
    root = tmp_path
    src = root / "vacation" / "day1" / "a.jpg"
    out = root / "renamed"
    d = resolve_destination_dir(
        root=root,
        output_dir=out,
        source_file=src,
        detected_source="WhatsApp",
        organise=False,
        flatten=False,
    )
    assert d == out / "vacation" / "day1"


def test_organise_inside_relative(tmp_path: Path) -> None:
    root = tmp_path
    src = root / "vacation" / "day1" / "a.jpg"
    out = root / "renamed"
    d = resolve_destination_dir(
        root=root,
        output_dir=out,
        source_file=src,
        detected_source="WhatsApp",
        organise=True,
        flatten=False,
    )
    assert d == out / "vacation" / "day1" / "WhatsApp"


def test_flatten_organise(tmp_path: Path) -> None:
    root = tmp_path
    src = root / "vacation" / "day1" / "a.jpg"
    out = root / "renamed"
    d = resolve_destination_dir(
        root=root,
        output_dir=out,
        source_file=src,
        detected_source="WhatsApp",
        organise=True,
        flatten=True,
    )
    assert d == out / "WhatsApp"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_organiser.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement**

```python
def resolve_destination_dir(
    *,
    root: Path,
    output_dir: Path,
    source_file: Path,
    detected_source: str,
    organise: bool,
    flatten: bool,
) -> Path:
    root = root.resolve()
    source_file = source_file.resolve()
    rel_parent = source_file.relative_to(root).parent
    parts: list[str] = []
    if not flatten and rel_parent != Path("."):
        parts.extend(rel_parent.parts)
    if organise:
        parts.append(detected_source)
    return output_dir.joinpath(*parts) if parts else output_dir
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_organiser.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/lupaxa/photo_renamer/organiser.py tests/test_organiser.py
git commit -m "$(cat <<'EOF'
Add output path organisation with flatten and source folders.

EOF
)"
```

---

### Task 7: Scanner

**Files:**
- Create: `src/lupaxa/photo_renamer/scanner.py`, `tests/test_scanner.py`

**Interfaces:**
- Consumes: `is_supported_extension`, `MediaFile`
- Produces: `scan_media(root: Path, *, recursive: bool, output_dir: Path, include: set[str] | None, exclude: set[str] | None) -> list[MediaFile]`  
  Collects matching files; skips anything under `output_dir.resolve()`; non-recursive = top-level files only; uses `os.scandir` / `Path.rglob` carefully.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_scanner.py
from pathlib import Path
from lupaxa.photo_renamer.scanner import scan_media


def test_scan_skips_output_and_respects_recursive(tmp_path: Path) -> None:
    (tmp_path / "a.jpg").write_bytes(b"x")
    nested = tmp_path / "sub"
    nested.mkdir()
    (nested / "b.jpg").write_bytes(b"x")
    out = tmp_path / "renamed"
    out.mkdir()
    (out / "c.jpg").write_bytes(b"x")

    top = scan_media(tmp_path, recursive=False, output_dir=out, include=None, exclude=None)
    assert {p.path.name for p in top} == {"a.jpg"}

    all_files = scan_media(tmp_path, recursive=True, output_dir=out, include=None, exclude=None)
    names = {p.path.name for p in all_files}
    assert names == {"a.jpg", "b.jpg"}
    assert "c.jpg" not in names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_scanner.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement `scan_media`**

Walk with `os.scandir` recursively when requested. Skip directories whose resolved path equals `output_dir` or is inside it. Build `MediaFile(path, extension, size)` for each match.

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_scanner.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/lupaxa/photo_renamer/scanner.py tests/test_scanner.py
git commit -m "$(cat <<'EOF'
Add media scanner that skips the output directory.

EOF
)"
```

---

### Task 8: Metadata extraction

**Files:**
- Create: `src/lupaxa/photo_renamer/metadata.py`, `tests/test_metadata.py`  
- Create fixtures under `tests/fixtures/` (minimal JPEG with EXIF if feasible; otherwise mock Pillow/`Image.open` / `pymediainfo`)

**Interfaces:**
- Consumes: `TimestampMode`, `TimestampResult`, `IMAGE_EXTENSIONS`, `VIDEO_EXTENSIONS`
- Produces: `extract_timestamp(path: Path, mode: TimestampMode, timezone: ZoneInfo | None) -> TimestampResult`  
  Image priority: DateTimeOriginal (36867) → DateTimeDigitized (36868) → DateTime (306) → mtime.  
  Video: MediaInfo creation/encoded date → mtime.  
  Mode `exif`: no filesystem fallback (`missing=True`, `value=None` if absent).  
  Mode `filesystem`: mtime only.  
  Mode `auto`: metadata then mtime.  
  Apply `timezone` conversion when `timezone` is not None and value is present. Register heif opener once at import.

- [ ] **Step 1: Write failing tests**

Prefer mocking to avoid binary fixtures fragility:

```python
# tests/test_metadata.py
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
from lupaxa.photo_renamer.metadata import extract_timestamp


def test_filesystem_mode_uses_mtime(tmp_path: Path) -> None:
    path = tmp_path / "a.jpg"
    path.write_bytes(b"not-a-real-jpeg")
    result = extract_timestamp(path, mode="filesystem", timezone=None)
    assert result.missing is False
    assert result.origin == "filesystem"
    assert result.value is not None


def test_exif_mode_missing_without_fallback(tmp_path: Path) -> None:
    path = tmp_path / "a.jpg"
    path.write_bytes(b"x")
    with patch("lupaxa.photo_renamer.metadata._read_image_exif_datetime", return_value=None):
        result = extract_timestamp(path, mode="exif", timezone=None)
    assert result.missing is True
    assert result.value is None
    assert result.origin == "none"


def test_auto_falls_back_to_filesystem(tmp_path: Path) -> None:
    path = tmp_path / "a.jpg"
    path.write_bytes(b"x")
    with patch("lupaxa.photo_renamer.metadata._read_image_exif_datetime", return_value=None):
        result = extract_timestamp(path, mode="auto", timezone=None)
    assert result.missing is False
    assert result.origin == "filesystem"
```

Add one test that parses a synthetic EXIF datetime string via a private helper `parse_exif_datetime("2026:08:01 14:55:22") == datetime(2026, 8, 1, 14, 55, 22)`.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_metadata.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement metadata module**

- Call `pillow_heif.register_heif_opener()` at module import (guarded try/except if unavailable in tests).
- `_read_image_exif_datetime(path) -> datetime | None` using `Image.open` + `getexif()` / `_getexif()` without loading pixels beyond what Pillow requires for EXIF.
- `_read_video_datetime(path) -> datetime | None` using `pymediainfo.MediaInfo.parse`.
- `extract_timestamp` orchestrates modes and optional `ZoneInfo` attach/convert (`dt.replace(tzinfo=timezone)` if naive, else `dt.astimezone(timezone)`), then return naive local wall time for naming **or** keep aware and have `format_timestamp` use the wall clock in that zone — pick one and document: **convert to target zone then use naive wall components for the filename**.

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_metadata.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/lupaxa/photo_renamer/metadata.py tests/test_metadata.py
git commit -m "$(cat <<'EOF'
Add image and video timestamp extraction with mode fallbacks.

EOF
)"
```

---

### Task 9: Config and CLI parsing

**Files:**
- Create: `src/lupaxa/photo_renamer/config.py`  
- Modify: `src/lupaxa/photo_renamer/cli.py` (parse only; wire run later)  
- Create: `tests/test_cli_parsing.py`

**Interfaces:**
- Consumes: enums/literals from models; `ConfigError`
- Produces:
  - `@dataclass(frozen=True) class AppConfig` with fields: `root: Path`, `output_dir: Path`, `recursive: bool`, `dry_run: bool`, `verbose: bool`, `quiet: bool`, `force: bool`, `skip_existing: bool`, `timestamp_mode: TimestampMode`, `name_format: NameFormat`, `organise: bool`, `flatten: bool`, `move: bool`, `include: set[str] | None`, `exclude: set[str] | None`, `timezone: ZoneInfo | None`, `log_file: Path | None`
  - `parse_args(argv: list[str] | None = None) -> AppConfig`
  - Resolves `output_dir`: if relative, `root / output`; default output name `"renamed"`
  - `--preserve-source` sets `name_format="source"` (if both `--format` and `--preserve-source`, last-wins via argparse or explicit rule: **if `--preserve-source` present, force source** unless `--format` explicitly provided after — simpler rule: `--preserve-source` means `name_format=source` and reject conflicting `--format` that is not `source` with `ConfigError`, OR treat preserve-source as alias by setting default and using `default=None` on format. **Chosen rule:** parse `--format` default `datetime`; if `--preserve-source`, set format to `source` (overrides default); if user also passed `--format`, `--format` wins when both present.)
  - `--include` / `--exclude`: comma-separated strings → sets
  - Mutual quiet/verbose: if both, `ConfigError`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_cli_parsing.py
from lupaxa.photo_renamer.config import parse_args


def test_defaults(tmp_path) -> None:
    cfg = parse_args([str(tmp_path)])
    assert cfg.root == tmp_path.resolve()
    assert cfg.output_dir == (tmp_path / "renamed").resolve()
    assert cfg.move is False
    assert cfg.name_format == "datetime"
    assert cfg.recursive is False


def test_preserve_source_alias(tmp_path) -> None:
    cfg = parse_args([str(tmp_path), "--preserve-source"])
    assert cfg.name_format == "source"


def test_format_wins_over_preserve_source(tmp_path) -> None:
    cfg = parse_args([str(tmp_path), "--preserve-source", "--format", "source-first"])
    assert cfg.name_format == "source-first"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_parsing.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement `config.py` argparse + `AppConfig`**

Wire `cli.parse_arguments` to call `parse_args`. Keep `main` returning 2 until pipeline exists, but parsing should work:

```python
def main(argv: list[str] | None = None) -> int:
    try:
        config = parse_args(argv)
    except ConfigError as exc:
        print(exc, file=sys.stderr)
        return 2
    # pipeline wired in Task 11
    ...
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_cli_parsing.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/lupaxa/photo_renamer/config.py src/lupaxa/photo_renamer/cli.py \
  tests/test_cli_parsing.py
git commit -m "$(cat <<'EOF'
Add AppConfig and CLI argument parsing.

EOF
)"
```

---

### Task 10: Reporting, progress, and log file

**Files:**
- Create: `src/lupaxa/photo_renamer/reporting.py`, `progress.py`, `tests/test_reporting.py`

**Interfaces:**
- Consumes: `AppConfig`, `RunStats`, `RenamePlan`
- Produces:
  - `print_startup(console: Console, config: AppConfig, file_count: int) -> None`
  - `print_summary(console: Console, stats: RunStats) -> None`
  - `LogWriter` context manager with `write_event(action: str, source: Path, destination: Path | None, source_label: str, origin: str, message: str = "") -> None`  
    Line format (tab-separated, undo-friendly):  
    `{iso_timestamp}\t{action}\t{source}\t{destination or -}\t{source_label}\t{origin}\t{message}`
  - `make_progress(console: Console, total: int, description: str) -> Progress` helper in `progress.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_reporting.py
from pathlib import Path
from lupaxa.photo_renamer.reporting import LogWriter


def test_log_writer_writes_tsv(tmp_path: Path) -> None:
    log = tmp_path / "rename.log"
    with LogWriter(log) as writer:
        writer.write_event(
            action="copy",
            source=Path("/a/b.jpg"),
            destination=Path("/a/renamed/2026-08-01_14-55-22.jpg"),
            source_label="WhatsApp",
            origin="filesystem",
            message="",
        )
    text = log.read_text(encoding="utf-8")
    assert "copy" in text
    assert "b.jpg" in text
    assert "WhatsApp" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_reporting.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement reporting + progress**

Use Rich `Table`, `Panel`, `Progress`. Honour quiet (skip startup/progress details) and verbose (caller prints per-file; reporting just provides helpers).

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_reporting.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/lupaxa/photo_renamer/reporting.py src/lupaxa/photo_renamer/progress.py \
  tests/test_reporting.py
git commit -m "$(cat <<'EOF'
Add Rich reporting helpers and TSV log writer.

EOF
)"
```

---

### Task 11: Pipeline execute (copy/move/dry-run)

**Files:**
- Create: `src/lupaxa/photo_renamer/pipeline.py`, `tests/test_pipeline.py`
- Modify: `src/lupaxa/photo_renamer/rename.py` — add `apply_plan(plan: RenamePlan, *, dry_run: bool) -> None`
- Modify: `src/lupaxa/photo_renamer/cli.py` — call `run(config) -> RunStats` and map exit codes

**Interfaces:**
- Consumes: all prior modules + `AppConfig`
- Produces:
  - `plan_file(media: MediaFile, config: AppConfig, reserved: set[Path]) -> RenamePlan`
  - `run(config: AppConfig, console: Console | None = None) -> RunStats`
  - Exit code: `0` if `stats.failed == 0` else `1`; config errors `2`

Behaviour for each file:
1. Optional skip via `skip_existing` + `is_already_named` (unless `force`)
2. `extract_timestamp`; if missing and mode requires it → fail plan / count failed + metadata_missing
3. `detect_source(media.path.name)`
4. `build_filename(...)`
5. `resolve_destination_dir(...)` + join filename
6. `ensure_unique(..., reserved=reserved)`; add dest to reserved; count collisions
7. action `copy` or `move` from config; dry-run skips filesystem write
8. `apply_plan`: `shutil.copy2` or `shutil.move`; create parent dirs; catch OSError → failed

- [ ] **Step 1: Write failing tests**

```python
# tests/test_pipeline.py
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from lupaxa.photo_renamer.config import AppConfig
from lupaxa.photo_renamer.models import TimestampResult
from lupaxa.photo_renamer.pipeline import run


def _cfg(root: Path, **kwargs: object) -> AppConfig:
    base = dict(
        root=root.resolve(),
        output_dir=(root / "renamed").resolve(),
        recursive=False,
        dry_run=False,
        verbose=False,
        quiet=True,
        force=False,
        skip_existing=False,
        timestamp_mode="filesystem",
        name_format="datetime",
        organise=False,
        flatten=False,
        move=False,
        include=None,
        exclude=None,
        timezone=None,
        log_file=None,
    )
    base.update(kwargs)
    return AppConfig(**base)  # type: ignore[arg-type]


def test_copy_preserves_original(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"abc")
    fixed = TimestampResult(
        value=datetime(2026, 8, 1, 13, 45, 22),
        origin="filesystem",
        missing=False,
    )
    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=fixed):
        stats = run(_cfg(tmp_path))
    assert stats.processed == 1
    assert src.exists()
    dest = tmp_path / "renamed" / "2026-08-01_13-45-22.jpg"
    assert dest.exists()
    assert dest.read_bytes() == b"abc"


def test_move_removes_original(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"abc")
    fixed = TimestampResult(
        value=datetime(2026, 8, 1, 13, 45, 22),
        origin="filesystem",
        missing=False,
    )
    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=fixed):
        stats = run(_cfg(tmp_path, move=True))
    assert not src.exists()
    assert (tmp_path / "renamed" / "2026-08-01_13-45-22.jpg").exists()


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"abc")
    fixed = TimestampResult(
        value=datetime(2026, 8, 1, 13, 45, 22),
        origin="filesystem",
        missing=False,
    )
    with patch("lupaxa.photo_renamer.pipeline.extract_timestamp", return_value=fixed):
        run(_cfg(tmp_path, dry_run=True))
    assert src.exists()
    assert not (tmp_path / "renamed").exists() or not any((tmp_path / "renamed").rglob("*"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_pipeline.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement pipeline + `apply_plan` + wire `cli.main`**

```python
def main(argv: list[str] | None = None) -> int:
    try:
        config = parse_args(argv)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    console = Console(quiet=config.quiet)
    stats = run(config, console=console)
    return 1 if stats.failed else 0
```

- [ ] **Step 4: Run full unit suite**

Run: `pytest -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/lupaxa/photo_renamer/pipeline.py src/lupaxa/photo_renamer/rename.py \
  src/lupaxa/photo_renamer/cli.py tests/test_pipeline.py
git commit -m "$(cat <<'EOF'
Wire end-to-end rename pipeline with copy, move, and dry-run.

EOF
)"
```

---

### Task 12: README and MkDocs

**Files:**
- Create: `README.md`, `mkdocs.yml`, `docs/index.md`, `docs/installation.md`, `docs/usage.md`, `docs/command-reference.md`, `docs/examples.md`, `docs/metadata.md`, `docs/source-detection.md`, `docs/organising.md`, `docs/troubleshooting.md`, `docs/development.md`
- Update: `README-PYPI.md` if needed

**Interfaces:**
- Consumes: finished CLI behaviour
- Produces: documentation covering installation, supported formats, examples, metadata behaviour, source detection, organising, troubleshooting, FAQ, development; note Rich screenshots as optional PNG assets under `docs/assets/` (placeholder caption if screenshot not captured yet)

- [ ] **Step 1: Write README sections**

Include: install (`pip install lupaxa-photo-renamer` / editable), quick start with `--dry-run`, flag summary, supported extensions, safety notes (copy default, never overwrite), troubleshooting, FAQ.

- [ ] **Step 2: Write MkDocs site**

`mkdocs.yml` with Material theme; nav matching the docs files above.

- [ ] **Step 3: Build docs**

Run: `mkdocs build --strict`  
Expected: success (fix warnings as errors if strict fails on missing links)

- [ ] **Step 4: Commit**

```bash
git add README.md README-PYPI.md mkdocs.yml docs
git commit -m "$(cat <<'EOF'
Add README and MkDocs documentation for photo-renamer.

EOF
)"
```

---

### Task 13: Quality gate pass

**Files:**
- Modify: any files needed to satisfy ruff/mypy/pytest
- Optionally add `src/lupaxa/photo_renamer/py.typed`

**Interfaces:**
- Consumes: complete package
- Produces: clean CI-local verification commands

- [ ] **Step 1: Add `py.typed` marker**

Create empty `src/lupaxa/photo_renamer/py.typed`.

- [ ] **Step 2: Run format/lint/type/tests**

```bash
ruff check src tests
ruff format --check src tests
mypy src
pytest
```

Expected: all pass with no warnings treated as errors by project config.

- [ ] **Step 3: Fix any issues**

Address failures minimally; re-run until green.

- [ ] **Step 4: Manual smoke**

```bash
photo-renamer --help
mkdir -p /tmp/pr-demo && printf 'x' > /tmp/pr-demo/IMG-20260801-WA0001.jpg
photo-renamer --dry-run --recursive /tmp/pr-demo
```

Expected: help text; dry-run shows planned copy into `renamed/`.

- [ ] **Step 5: Commit**

```bash
git add -u src tests
git add src/lupaxa/photo_renamer/py.typed
git commit -m "$(cat <<'EOF'
Satisfy ruff, mypy, and final quality gates.

EOF
)"
```

---

## Self-review checklist (plan author)

1. **Spec coverage:** Packaging, CLI flags, metadata priority, sources, formats, collisions, organise/flatten, copy/move/dry-run, Rich + log, tests, README/MkDocs, LICENCE — each maps to Tasks 1–13. Future enhancements explicitly out of scope.
2. **Placeholders:** None intentional; Signal patterns and already-named regexes specified.
3. **Type consistency:** `AppConfig`, `TimestampResult`, `RenamePlan`, `RunStats`, `NameFormat`, `TimestampMode` used consistently across Tasks 2–11.

## Execution handoff

Plan complete and saved to `cursor-docs/superpowers/plans/2026-08-02-photo-renamer.md`. Two execution options:

**1. Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks, fast iteration  

**2. Inline Execution** — execute tasks in this session using executing-plans, batch execution with checkpoints  

Which approach?
