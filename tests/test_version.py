from lupaxa.photo_renamer.version import __version__, get_version


def test_get_version_matches_dunder() -> None:
    assert __version__ == "0.1.0"
    assert get_version() == __version__
