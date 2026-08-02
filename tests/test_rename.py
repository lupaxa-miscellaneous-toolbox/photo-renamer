from datetime import datetime

from lupaxa.photo_renamer.rename import build_filename, is_already_named


def test_build_filename_formats() -> None:
    dt = datetime(2026, 8, 1, 14, 55, 22)
    assert build_filename(dt, "JPG", "datetime", "WhatsApp") == "2026-08-01_14-55-22.jpg"
    assert build_filename(dt, "jpg", "source", "WhatsApp") == "2026-08-01_14-55-22_WhatsApp.jpg"
    assert (
        build_filename(dt, "jpg", "source-first", "WhatsApp")
        == "WhatsApp_2026-08-01_14-55-22.jpg"
    )


def test_is_already_named() -> None:
    assert is_already_named("2026-08-01_14-55-22.jpg") is True
    assert is_already_named("2026-08-01_14-55-22_001.jpg") is True
    assert is_already_named("2026-08-01_14-55-22_WhatsApp.jpg") is True
    assert is_already_named("WhatsApp_2026-08-01_14-55-22.jpg") is True
    assert is_already_named("IMG-20260801-WA0001.jpg") is False
