import os
from pathlib import Path

import pytest

from lupaxa.photo_renamer.scanner import ScanError, scan_media


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


def test_recursive_scan_skips_unreadable_directory_and_continues(tmp_path: Path) -> None:
    sibling = tmp_path / "sibling.jpg"
    sibling.write_bytes(b"x")
    unreadable = tmp_path / "unreadable"
    unreadable.mkdir()
    (unreadable / "hidden.jpg").write_bytes(b"x")
    errors: list[ScanError] = []

    unreadable.chmod(0)
    try:
        try:
            with os.scandir(unreadable):
                pass
        except PermissionError:
            pass
        else:
            pytest.skip("chmod 000 does not deny directory access for this user")

        files = scan_media(
            tmp_path,
            recursive=True,
            output_dir=tmp_path / "renamed",
            include=None,
            exclude=None,
            errors=errors,
        )
    finally:
        unreadable.chmod(0o700)

    assert {media.path for media in files} == {sibling}
    assert len(errors) == 1
    assert errors[0].path == unreadable
