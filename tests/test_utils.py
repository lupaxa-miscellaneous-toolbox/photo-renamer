from lupaxa.photo_renamer.utils import is_supported_extension, normalize_extension


def test_normalize_extension_strips_dot_and_lowercases() -> None:
    assert normalize_extension(".JPG") == "jpg"
    assert normalize_extension("HEIC") == "heic"


def test_is_supported_respects_include_exclude() -> None:
    assert is_supported_extension("jpg", include=None, exclude=None) is True
    assert is_supported_extension("gif", include=None, exclude=None) is False
    assert is_supported_extension("gif", include={"gif"}, exclude=None) is False
    assert is_supported_extension("jpg", include={"png"}, exclude=None) is False
    assert is_supported_extension("jpg", include=None, exclude={"jpg"}) is False
