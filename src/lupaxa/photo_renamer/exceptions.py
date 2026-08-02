"""Exceptions for lupaxa.photo_renamer."""

from __future__ import annotations


class PhotoRenamerError(Exception):
    """Base error for photo-renamer."""


class ConfigError(PhotoRenamerError):
    """Invalid configuration or CLI arguments."""


class MetadataError(PhotoRenamerError):
    """Failed to read media metadata when required."""


class FileOperationError(PhotoRenamerError):
    """Copy/move/filesystem failure for a single file."""
