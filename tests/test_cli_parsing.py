from pathlib import Path
from unittest.mock import patch

import pytest

from lupaxa.photo_renamer.cli import main
from lupaxa.photo_renamer.config import parse_args
from lupaxa.photo_renamer.exceptions import ConfigError
from lupaxa.photo_renamer.models import RunStats


def test_defaults(tmp_path: Path) -> None:
    cfg = parse_args([str(tmp_path)])
    assert cfg.root == tmp_path.resolve()
    assert cfg.output_dir == (tmp_path / "renamed").resolve()
    assert cfg.move is False
    assert cfg.name_format == "datetime"
    assert cfg.recursive is False


def test_preserve_source_alias(tmp_path: Path) -> None:
    cfg = parse_args([str(tmp_path), "--preserve-source"])
    assert cfg.name_format == "source"


def test_format_wins_over_preserve_source(tmp_path: Path) -> None:
    cfg = parse_args([str(tmp_path), "--preserve-source", "--format", "source-first"])
    assert cfg.name_format == "source-first"


def test_main_maps_pipeline_failure_to_exit_one(tmp_path: Path) -> None:
    with patch("lupaxa.photo_renamer.cli.run", return_value=RunStats(failed=1)):
        assert main([str(tmp_path), "--quiet"]) == 1


def test_main_maps_config_error_to_exit_two(tmp_path: Path) -> None:
    assert main([str(tmp_path), "--quiet", "--verbose"]) == 2


@pytest.mark.parametrize("path_kind", ["missing", "file"])
def test_parse_args_rejects_path_that_is_not_directory(
    tmp_path: Path,
    path_kind: str,
) -> None:
    path = tmp_path / path_kind
    if path_kind == "file":
        path.write_bytes(b"x")

    with pytest.raises(ConfigError, match="directory"):
        parse_args([str(path)])


def test_parse_args_rejects_unknown_include_extension(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="unsupported --include extension: gif"):
        parse_args([str(tmp_path), "--include", "jpg,gif"])


def test_timezone_value_error_is_config_error(tmp_path: Path) -> None:
    with (
        patch("lupaxa.photo_renamer.config.ZoneInfo", side_effect=ValueError("bad key")),
        pytest.raises(ConfigError, match="unknown timezone"),
    ):
        parse_args([str(tmp_path), "--timezone", "Bad/Zone"])
