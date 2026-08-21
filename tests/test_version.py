import re

from lupaxa.photo_renamer.version import __version__, get_version

_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")


def test_version_is_semver() -> None:
    assert isinstance(__version__, str)
    assert _SEMVER.fullmatch(__version__)


def test_get_version_matches_dunder() -> None:
    assert get_version() == __version__
