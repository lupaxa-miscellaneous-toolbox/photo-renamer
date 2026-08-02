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
