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
