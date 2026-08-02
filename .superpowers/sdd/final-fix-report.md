# Final Fix Report

## Whole-branch Critical and Important findings

### Changes

- Made recursive scanning isolate `OSError` failures per directory, continue scanning siblings,
  report scan errors to the pipeline, and count each scan error in `RunStats.failed`.
- Validated the input path as an existing directory and rejected unknown `--include` extensions
  with `ConfigError`; include filters now intersect the supported extension set.
- Expanded exclusive-move fallback to `EXDEV`, `EPERM`, `EOPNOTSUPP`, and `ENOSYS`.
- Converted timezone `ValueError` failures to `ConfigError`.
- Removed `src/lupaxa/__init__.py` for a PEP 420 namespace package and configured mypy with
  `mypy_path = "src"` plus explicit package bases.
- Fixed dangling-symlink parametrization and added regression coverage for all findings.

### Commands and results

- `python -m pytest tests/test_utils.py tests/test_cli_parsing.py tests/test_rename.py` before
  implementation: 8 failed, 8 passed; failures reproduced extension, path, timezone, and move
  fallback defects.
- `python -m pytest tests/test_utils.py tests/test_cli_parsing.py tests/test_rename.py
  tests/test_scanner.py tests/test_pipeline.py`: 32 passed.
- First full gate run: pytest passed 65 tests; Ruff found one formatting violation; mypy exposed
  duplicate namespace-package module resolution. Both gate findings were corrected.
- `python -m ruff check .`: passed (`All checks passed!`).
- `python -m ruff format --check .`: passed (`28 files already formatted`).
- `python -m mypy src`: passed (`Success: no issues found in 17 source files`).
- `python -m pytest`: passed (`65 passed in 0.23s`, 90% total coverage).
- `python -c "import lupaxa.photo_renamer as package; print(package.version())"`: passed and
  printed `0.1.0`.
