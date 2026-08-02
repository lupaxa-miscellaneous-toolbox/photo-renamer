"""Shared constants for lupaxa.photo_renamer."""

from __future__ import annotations

IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {"jpg", "jpeg", "png", "heic", "heif", "webp", "tif", "tiff"}
)
VIDEO_EXTENSIONS: frozenset[str] = frozenset({"mp4", "mov", "avi", "mkv", "m4v", "3gp"})
DEFAULT_EXTENSIONS: frozenset[str] = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

SOURCE_LABELS: tuple[str, ...] = (
    "WhatsApp",
    "Telegram",
    "Signal",
    "Pixel",
    "Samsung",
    "iPhone",
    "Screenshot",
    "Camera",
    "Unknown",
)
