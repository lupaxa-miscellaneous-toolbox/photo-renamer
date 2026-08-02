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
