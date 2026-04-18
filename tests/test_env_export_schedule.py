"""Tests for envctl.env_export_schedule."""
from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from envctl.env_export_schedule import ScheduleConfig, ScheduleError, _write_export, run_schedule


_PROFILE_VARS = {"APP_ENV": "prod", "PORT": "8080"}


def _mock_get(name):
    if name == "prod":
        return _PROFILE_VARS
    return None


def _mock_export(vars_, fmt):
    return "\n".join(f"{k}={v}" for k, v in vars_.items())


@pytest.fixture()
def tmp_out(tmp_path):
    return tmp_path / "out.env"


def test_write_export_creates_file(tmp_out):
    with patch("envctl.env_export_schedule.get_profile", side_effect=_mock_get), \
         patch("envctl.env_export_schedule.export_profile", side_effect=_mock_export):
        cfg = ScheduleConfig(profile="prod", output_path=tmp_out)
        _write_export(cfg)
    assert tmp_out.exists()
    assert "APP_ENV=prod" in tmp_out.read_text()


def test_write_export_missing_profile_raises(tmp_out):
    with patch("envctl.env_export_schedule.get_profile", return_value=None):
        cfg = ScheduleConfig(profile="ghost", output_path=tmp_out)
        with pytest.raises(ScheduleError, match="not found"):
            _write_export(cfg)


def test_write_export_calls_on_write(tmp_out):
    callback = MagicMock()
    with patch("envctl.env_export_schedule.get_profile", side_effect=_mock_get), \
         patch("envctl.env_export_schedule.export_profile", side_effect=_mock_export):
        cfg = ScheduleConfig(profile="prod", output_path=tmp_out, on_write=callback)
        _write_export(cfg)
    callback.assert_called_once_with(tmp_out)


def test_run_schedule_respects_max_runs(tmp_out):
    sleep_calls = []
    with patch("envctl.env_export_schedule.get_profile", side_effect=_mock_get), \
         patch("envctl.env_export_schedule.export_profile", side_effect=_mock_export):
        cfg = ScheduleConfig(profile="prod", output_path=tmp_out, interval=5, max_runs=3)
        run_schedule(cfg, _sleep=lambda s: sleep_calls.append(s))
    assert len(sleep_calls) == 2  # sleeps between runs, not after last


def test_run_schedule_uses_interval(tmp_out):
    sleep_calls = []
    with patch("envctl.env_export_schedule.get_profile", side_effect=_mock_get), \
         patch("envctl.env_export_schedule.export_profile", side_effect=_mock_export):
        cfg = ScheduleConfig(profile="prod", output_path=tmp_out, interval=42, max_runs=2)
        run_schedule(cfg, _sleep=lambda s: sleep_calls.append(s))
    assert all(s == 42 for s in sleep_calls)


def test_run_schedule_creates_parent_dirs(tmp_path):
    out = tmp_path / "deep" / "nested" / "out.env"
    with patch("envctl.env_export_schedule.get_profile", side_effect=_mock_get), \
         patch("envctl.env_export_schedule.export_profile", side_effect=_mock_export):
        cfg = ScheduleConfig(profile="prod", output_path=out, max_runs=1)
        run_schedule(cfg, _sleep=lambda s: None)
    assert out.exists()
