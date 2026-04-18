"""Tests for envctl.cli_export_schedule."""
from __future__ import annotations

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from envctl.cli_export_schedule import cmd_schedule


@pytest.fixture()
def runner():
    return CliRunner()


def _noop_run(config, _sleep=None):
    pass


def test_schedule_run_success(runner, tmp_path):
    out = str(tmp_path / "out.env")
    with patch("envctl.cli_export_schedule.run_schedule", side_effect=_noop_run):
        result = runner.invoke(cmd_schedule, ["run", "prod", out, "--runs", "1"])
    assert result.exit_code == 0


def test_schedule_run_default_fmt(runner, tmp_path):
    out = str(tmp_path / "out.env")
    captured = {}
    def capture(config, _sleep=None):
        captured["fmt"] = config.fmt
    with patch("envctl.cli_export_schedule.run_schedule", side_effect=capture):
        runner.invoke(cmd_schedule, ["run", "prod", out, "--runs", "1"])
    assert captured.get("fmt") == "dotenv"


def test_schedule_run_custom_interval(runner, tmp_path):
    out = str(tmp_path / "out.env")
    captured = {}
    def capture(config, _sleep=None):
        captured["interval"] = config.interval
    with patch("envctl.cli_export_schedule.run_schedule", side_effect=capture):
        runner.invoke(cmd_schedule, ["run", "prod", out, "--interval", "30", "--runs", "1"])
    assert captured.get("interval") == 30


def test_schedule_run_error_shown(runner, tmp_path):
    from envctl.env_export_schedule import ScheduleError
    out = str(tmp_path / "out.env")
    with patch("envctl.cli_export_schedule.run_schedule",
               side_effect=ScheduleError("Profile 'x' not found.")):
        result = runner.invoke(cmd_schedule, ["run", "x", out])
    assert result.exit_code != 0
    assert "not found" in result.output
