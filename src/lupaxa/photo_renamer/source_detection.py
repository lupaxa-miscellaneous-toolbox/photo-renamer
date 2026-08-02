"""Filename pattern matching for media source detection."""

from __future__ import annotations

import re
from pathlib import Path

from lupaxa.photo_renamer.constants import SOURCE_LABELS

(
    WHATSAPP,
    TELEGRAM,
    SIGNAL,
    PIXEL,
    SAMSUNG,
    IPHONE,
    SCREENSHOT,
    CAMERA,
    UNKNOWN,
) = SOURCE_LABELS

_FLAGS = re.IGNORECASE

_RULES: tuple[tuple[str, tuple[re.Pattern[str], ...]], ...] = (
    (
        WHATSAPP,
        (
            re.compile(r"^IMG-.*-WA", _FLAGS),
            re.compile(r"^VID-.*-WA", _FLAGS),
        ),
    ),
    (
        TELEGRAM,
        (
            re.compile(r"^Photo_", _FLAGS),
            re.compile(r"^Video_", _FLAGS),
        ),
    ),
    (
        SIGNAL,
        (
            re.compile(r"^signal-", _FLAGS),
            re.compile(r"^Signal-", _FLAGS),
            re.compile(r"_signal(\.|$)", _FLAGS),
        ),
    ),
    (PIXEL, (re.compile(r"^PXL_", _FLAGS),)),
    (SAMSUNG, (re.compile(r"^\d{8}_", _FLAGS),)),
    (IPHONE, (re.compile(r"^IMG_\d{4}", _FLAGS),)),
    (
        SCREENSHOT,
        (
            re.compile(r"^Screenshot", _FLAGS),
            re.compile(r"^Screen Shot", _FLAGS),
            re.compile(r"^Screen_", _FLAGS),
        ),
    ),
    (
        CAMERA,
        (
            re.compile(r"^DSC_", _FLAGS),
            re.compile(r"^DSCF", _FLAGS),
        ),
    ),
)


def detect_source(filename: str) -> str:
    """Return the detected media source label for *filename*."""
    name = Path(filename).name
    for label, patterns in _RULES:
        for pattern in patterns:
            if pattern.search(name):
                return label
    return UNKNOWN
