"""Tests for envctl.env_summarize."""

from __future__ import annotations

import pytest

from envctl.env_summarize import (
    SummarizeError,
    ProfileSummary,
    format_summary,
    summarize_all_profiles,
    summarize_profile,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

_PROFILES = {
    "dev": {"APP_HOST": "localhost", "APP_PORT": "8080", "DEBUG": ""},
    "prod": {"APP_HOST": "example.com", "APP_PORT": "443"},
    "empty": {},
}


def _mock_get(name):
    return _PROFILES.get(name)


def _mock_load():
    return _PROFILES


# ---------------------------------------------------------------------------
# summarize_profile
# ---------------------------------------------------------------------------

def test_summarize_profile_total_keys(monkeypatch):
    monkeypatch.setattr("envctl.env_summarize.get_profile", _mock_get)
    s = summarize_profile("dev")
    assert s.total_keys == 3


def test_summarize_profile_detects_empty_keys(monkeypatch):
    monkeypatch.setattr("envctl.env_summarize.get_profile", _mock_get)
    s = summarize_profile("dev")
    assert "DEBUG" in s.empty_keys


def test_summarize_profile_no_empty_keys(monkeypatch):
    monkeypatch.setattr("envctl.env_summarize.get_profile", _mock_get)
    s = summarize_profile("prod")
    assert s.empty_keys == []


def test_summarize_profile_longest_and_shortest_key(monkeypatch):
    monkeypatch.setattr("envctl.env_summarize.get_profile", _mock_get)
    s = summarize_profile("dev")
    assert s.longest_key in ("APP_HOST", "APP_PORT")  # both length 8
    assert s.shortest_key == "DEBUG"


def test_summarize_profile_unique_values(monkeypatch):
    monkeypatch.setattr("envctl.env_summarize.get_profile", _mock_get)
    s = summarize_profile("dev")
    # "localhost" and "8080" are unique ("" excluded)
    assert s.unique_values == 2


def test_summarize_profile_empty_profile(monkeypatch):
    monkeypatch.setattr("envctl.env_summarize.get_profile", _mock_get)
    s = summarize_profile("empty")
    assert s.total_keys == 0
    assert s.longest_key is None
    assert s.avg_key_length == 0.0


def test_summarize_profile_missing_raises(monkeypatch):
    monkeypatch.setattr("envctl.env_summarize.get_profile", lambda _: None)
    with pytest.raises(SummarizeError, match="does not exist"):
        summarize_profile("ghost")


# ---------------------------------------------------------------------------
# summarize_all_profiles
# ---------------------------------------------------------------------------

def test_summarize_all_profiles_returns_all(monkeypatch):
    monkeypatch.setattr("envctl.env_summarize.get_profile", _mock_get)
    monkeypatch.setattr("envctl.env_summarize.load_profiles", _mock_load)
    result = summarize_all_profiles()
    assert set(result.keys()) == {"dev", "prod", "empty"}


def test_summarize_all_profiles_empty_store(monkeypatch):
    monkeypatch.setattr("envctl.env_summarize.load_profiles", lambda: {})
    assert summarize_all_profiles() == {}


# ---------------------------------------------------------------------------
# format_summary
# ---------------------------------------------------------------------------

def test_format_summary_contains_profile_name():
    s = ProfileSummary(name="dev", total_keys=2)
    out = format_summary(s)
    assert "dev" in out


def test_format_summary_lists_empty_keys():
    s = ProfileSummary(name="dev", total_keys=3, empty_keys=["DEBUG"])
    out = format_summary(s)
    assert "DEBUG" in out
