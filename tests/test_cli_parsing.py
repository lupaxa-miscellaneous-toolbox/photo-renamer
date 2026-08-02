from pathlib import Path

from lupaxa.photo_renamer.config import parse_args


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
