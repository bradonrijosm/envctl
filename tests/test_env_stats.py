"""Tests for envctl.env_stats."""
import pytest
from unittest.mock import patch
from envctl.env_stats import (
    StatsError,
    ProfileStats,
    profile_stats,
    all_stats,
    summary_report,
)

_PROFILES = {
    "dev": {"variables": {"HOST": "localhost", "PORT": "8080", "DEBUG": ""}},
    "prod": {"variables": {"HOST": "example.com", "PORT": "443"}},
}


def _mock_get(name):
    return _PROFILES.get(name)


def _mock_load():
    return _PROFILES


def test_profile_stats_var_count():
    with patch("envctl.env_stats.get_profile", side_effect=_mock_get):
        s = profile_stats("dev")
    assert s.var_count == 3


def test_profile_stats_empty_count():
    with patch("envctl.env_stats.get_profile", side_effect=_mock_get):
        s = profile_stats("dev")
    assert s.empty_count == 1


def test_profile_stats_no_empty():
    with patch("envctl.env_stats.get_profile", side_effect=_mock_get):
        s = profile_stats("prod")
    assert s.empty_count == 0


def test_profile_stats_avg_key_length():
    with patch("envctl.env_stats.get_profile", side_effect=_mock_get):
        s = profile_stats("prod")
    expected = (len("HOST") + len("PORT")) / 2
    assert s.avg_key_length == pytest.approx(expected)


def test_profile_stats_missing_raises():
    with patch("envctl.env_stats.get_profile", return_value=None):
        with pytest.raises(StatsError, match="not found"):
            profile_stats("ghost")


def test_all_stats_returns_list():
    with patch("envctl.env_stats.get_profile", side_effect=_mock_get), \
         patch("envctl.env_stats.load_profiles", side_effect=_mock_load):
        result = all_stats()
    assert len(result) == 2
    names = {s.name for s in result}
    assert names == {"dev", "prod"}


def test_summary_report_contains_headers():
    stats = [ProfileStats(name="dev", var_count=3, empty_count=1,
                          key_lengths=[4, 4, 5], value_lengths=[9, 4, 0])]
    report = summary_report(stats)
    assert "Profile" in report
    assert "dev" in report


def test_summary_report_empty():
    assert summary_report([]) == "No profiles found."


def test_profile_stats_empty_profile():
    with patch("envctl.env_stats.get_profile", return_value={"variables": {}}):
        s = profile_stats("empty")
    assert s.var_count == 0
    assert s.avg_key_length == 0.0
    assert s.avg_value_length == 0.0
    assert s.longest_key is None
