import pytest

from lupaxa.photo_renamer.source_detection import detect_source


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("IMG-20260801-WA0001.jpg", "WhatsApp"),
        ("VID-20260801-WA0002.mp4", "WhatsApp"),
        ("Photo_12345.jpg", "Telegram"),
        ("Video_12345.mp4", "Telegram"),
        ("signal-2026-08-01-123456.jpg", "Signal"),
        ("PXL_20260801_135522.jpg", "Pixel"),
        ("20260801_135522.jpg", "Samsung"),
        ("IMG_1234.JPG", "iPhone"),
        ("Screenshot 2026-08-01.png", "Screenshot"),
        ("Screen Shot 2026-08-01.png", "Screenshot"),
        ("Screen_001.png", "Screenshot"),
        ("DSC_0123.jpg", "Camera"),
        ("DSCF0001.JPG", "Camera"),
        ("holiday.jpg", "Unknown"),
    ],
)
def test_detect_source(name: str, expected: str) -> None:
    assert detect_source(name) == expected
