# Development

## Set up a checkout

Python 3.13 or newer is required.

```bash
git clone https://github.com/lupaxa-code-playground/photo-renamer.git
cd photo-renamer
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

The package uses a `src/` layout and Hatchling. The console entry point is
`lupaxa.photo_renamer.cli:main`.

## Run checks

```bash
pytest
ruff check .
mypy src
mkdocs build --strict
```

Serve the documentation with live reload:

```bash
mkdocs serve
```

## Architecture

The processing flow is:

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

Modules keep these responsibilities separate so metadata readers, source rules, and output
policies can be tested independently. The scanner excludes the output tree and does not follow
symlinks. Execution handles files one at a time and continues after per-file I/O errors.

## Documentation

Keep README examples and MkDocs pages aligned with the implemented CLI. In particular:

- copy remains the default and moving requires `--move`;
- relative output defaults to `PATH/renamed/`;
- `--organise` nests source inside the relative path;
- `--flatten` removes relative paths; and
- `--preserve-source` aliases `--format source`.

## License

The project is available under the MIT License. The canonical license text is the repository
file named `LICENCE`.
