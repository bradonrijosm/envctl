"""Tests for envctl.cli_stats CLI commands."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envctl.cli_stats import cmd_stats
from envctl.env_stats import ProfileStats, StatsError


@pytest.fixture
def runner():
    return CliRunner()


_STAT = ProfileStats(
    name="dev",
    var_count=3,
    empty_count=1,
    key_lengths=[4, 4, 5],
    value_lengths=[9, 4, 0],
)


def test_stats_show_success(runner):
    with patch("envctl.cli_stats.profile_stats", return_value=_STAT):
        result = runner.invoke(cmd_stats, ["show", "dev"])
    assert result.exit_code == 0
    assert "Variables" in result.output
    assert "3" in result.output


def test_stats_show_missing_profile(runner):
    with patch("envctl.cli_stats.profile_stats", side_effect=StatsError("Profile 'x' not found.")):
        result = runner.invoke(cmd_stats, ["show", "x"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_stats_summary_success(runner):
    with patch("envctl.cli_stats.all_stats", return_value=[_STAT]):
        with patch("envctl.cli_stats.summary_report", return_value="REPORT"):
            result = runner.invoke(cmd_stats, ["summary"])
    assert result.exit_code == 0
    assert "REPORT" in result.output


def test_stats_summary_empty(runner):
    with patch("envctl.cli_stats.all_stats", return_value=[]):
        with patch("envctl.cli_stats.summary_report", return_value="No profiles found."):
            result = runner.invoke(cmd_stats, ["summary"])
    assert result.exit_code == 0
    assert "No profiles found." in result.output
