from pathlib import Path
from unittest.mock import patch

from lupaxa.photo_renamer.cli import main
from lupaxa.photo_renamer.config import parse_args
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
