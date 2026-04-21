"""Tests for envctl.env_filter."""

from __future__ import annotations

import pytest

from envctl.env_filter import FilterError, apply_filter, filter_profile


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

_VARS = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.example.com",
    "DB_PASSWORD": "secret",
    "DEBUG": "true",
}


def _mock_get(monkeypatch, variables: dict | None):
    monkeypatch.setattr("envctl.env_filter.get_profile", lambda _name: variables)


def _mock_set(monkeypatch, captured: list):
    monkeypatch.setattr("envctl.env_filter.set_profile", lambda name, v: captured.append((name, v)))


# ---------------------------------------------------------------------------
# filter_profile
# ---------------------------------------------------------------------------

def test_filter_by_key_prefix(monkeypatch):
    _mock_get(monkeypatch, _VARS)
    result = filter_profile("dev", key_pattern="APP_*")
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_filter_by_value_pattern(monkeypatch):
    _mock_get(monkeypatch, _VARS)
    result = filter_profile("dev", value_pattern="*host*", case_sensitive=False)
    assert "APP_HOST" in result
    assert "DB_HOST" in result


def test_filter_invert_returns_non_matching(monkeypatch):
    _mock_get(monkeypatch, _VARS)
    result = filter_profile("dev", key_pattern="DB_*", invert=True)
    assert "DB_HOST" not in result
    assert "DB_PASSWORD" not in result
    assert "APP_HOST" in result


def test_filter_case_sensitive_no_match(monkeypatch):
    _mock_get(monkeypatch, _VARS)
    result = filter_profile("dev", key_pattern="app_*", case_sensitive=True)
    assert result == {}


def test_filter_case_insensitive_matches(monkeypatch):
    _mock_get(monkeypatch, _VARS)
    result = filter_profile("dev", key_pattern="app_*", case_sensitive=False)
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_filter_no_pattern_raises(monkeypatch):
    _mock_get(monkeypatch, _VARS)
    with pytest.raises(FilterError, match="At least one"):
        filter_profile("dev")


def test_filter_missing_profile_raises(monkeypatch):
    _mock_get(monkeypatch, None)
    with pytest.raises(FilterError, match="does not exist"):
        filter_profile("ghost", key_pattern="*")


def test_filter_key_and_value_combined(monkeypatch):
    _mock_get(monkeypatch, _VARS)
    result = filter_profile("dev", key_pattern="*HOST*", value_pattern="*example*")
    assert result == {"DB_HOST": "db.example.com"}


# ---------------------------------------------------------------------------
# apply_filter
# ---------------------------------------------------------------------------

def test_apply_filter_persists(monkeypatch):
    saved: list = []
    _mock_get(monkeypatch, _VARS)
    _mock_set(monkeypatch, saved)
    kept = apply_filter("dev", key_pattern="APP_*")
    assert len(saved) == 1
    name, variables = saved[0]
    assert name == "dev"
    assert variables == kept


def test_apply_filter_returns_kept_vars(monkeypatch):
    _mock_get(monkeypatch, _VARS)
    _mock_set(monkeypatch, [])
    kept = apply_filter("dev", key_pattern="DB_*")
    assert set(kept.keys()) == {"DB_HOST", "DB_PASSWORD"}
