from __future__ import annotations

import io
from unittest.mock import patch

import pytest

from lupaxa.photo_renamer.exceptions import ConfigError
from lupaxa.photo_renamer.workers import confirm_workers, recommended_max_workers


def test_recommended_max_workers_is_cpu_times_two() -> None:
    with patch("lupaxa.photo_renamer.workers.os.cpu_count", return_value=4):
        assert recommended_max_workers() == 8


def test_recommended_max_workers_falls_back_when_cpu_count_none() -> None:
    with patch("lupaxa.photo_renamer.workers.os.cpu_count", return_value=None):
        assert recommended_max_workers() == 2


def test_confirm_workers_noop_when_within_cap() -> None:
    with patch("lupaxa.photo_renamer.workers.recommended_max_workers", return_value=8):
        confirm_workers(8, assume_yes=False)  # must not raise


def test_confirm_workers_skips_prompt_with_assume_yes() -> None:
    stdin = io.StringIO("")
    stderr = io.StringIO()
    with patch("lupaxa.photo_renamer.workers.recommended_max_workers", return_value=2):
        confirm_workers(99, assume_yes=True, stdin=stdin, stderr=stderr)
    assert stdin.read() == ""
    assert stderr.getvalue() == ""


def test_confirm_workers_accepts_yes_on_tty() -> None:
    stdin = io.StringIO("yes\n")
    stderr = io.StringIO()
    with (
        patch("lupaxa.photo_renamer.workers.recommended_max_workers", return_value=2),
        patch.object(stdin, "isatty", return_value=True),
    ):
        confirm_workers(8, assume_yes=False, stdin=stdin, stderr=stderr)
    assert "exceeds recommended max 2" in stderr.getvalue()


def test_confirm_workers_declines_empty_on_tty() -> None:
    stdin = io.StringIO("\n")
    stderr = io.StringIO()
    with (
        patch("lupaxa.photo_renamer.workers.recommended_max_workers", return_value=2),
        patch.object(stdin, "isatty", return_value=True),
        pytest.raises(ConfigError, match="cancelled"),
    ):
        confirm_workers(8, assume_yes=False, stdin=stdin, stderr=stderr)


def test_confirm_workers_non_tty_requires_yes() -> None:
    stdin = io.StringIO("yes\n")
    stderr = io.StringIO()
    with (
        patch("lupaxa.photo_renamer.workers.recommended_max_workers", return_value=2),
        patch.object(stdin, "isatty", return_value=False),
        pytest.raises(ConfigError, match="--yes"),
    ):
        confirm_workers(8, assume_yes=False, stdin=stdin, stderr=stderr)
