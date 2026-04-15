"""Tests for envctl.cli_watch."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envctl.cli_watch import cmd_watch
from envctl.watch import WatchError


@pytest.fixture
def runner():
    return CliRunner()


def test_watch_start_missing_profile(runner):
    with patch(
        "envctl.cli_watch.watch_profile",
        side_effect=WatchError("Profile 'ghost' does not exist."),
    ):
        result = runner.invoke(cmd_watch, ["start", "ghost"])

    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_watch_start_calls_watch_profile(runner):
    with patch("envctl.cli_watch.watch_profile") as mock_watch:
        result = runner.invoke(cmd_watch, ["start", "myprofile", "--interval", "0.5"])

    mock_watch.assert_called_once()
    args, kwargs = mock_watch.call_args
    assert args[0] == "myprofile"
    assert kwargs.get("interval") == pytest.approx(0.5)


def test_watch_start_default_interval(runner):
    with patch("envctl.cli_watch.watch_profile") as mock_watch:
        runner.invoke(cmd_watch, ["start", "dev"])

    _, kwargs = mock_watch.call_args
    assert kwargs.get("interval") == pytest.approx(2.0)


def test_watch_start_prints_banner(runner):
    with patch("envctl.cli_watch.watch_profile"):
        result = runner.invoke(cmd_watch, ["start", "staging"])

    assert "staging" in result.output
    assert "Ctrl+C" in result.output
