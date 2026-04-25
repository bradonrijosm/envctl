"""Tests for envctl.env_count."""

from __future__ import annotations

import pytest

from envctl.env_count import CountError, ProfileCount, count_all_profiles, count_profile


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _mock_get(monkeypatch, variables):
    """Patch get_profile to return the given variables dict for any profile name."""
    monkeypatch.setattr("envctl.env_count.get_profile", lambda _name: variables)


def _mock_load(monkeypatch, profiles):
    """Patch load_profiles and get_profile to use the given profiles dict."""
    monkeypatch.setattr("envctl.env_count.load_profiles", lambda: profiles)
    # Also patch get_profile so count_profile works per-name
    monkeypatch.setattr(
        "envctl.env_count.get_profile",
        lambda name: profiles.get(name),
    )


# ---------------------------------------------------------------------------
# count_profile
# ---------------------------------------------------------------------------

def test_count_profile_total(monkeypatch):
    _mock_get(monkeypatch, {"A": "1", "B": "2", "C": ""})
    pc = count_profile("myprofile")
    assert pc.total == 3


def test_count_profile_empty_and_non_empty(monkeypatch):
    _mock_get(monkeypatch, {"A": "", "B": "", "C": "hello"})
    pc = count_profile("myprofile")
    assert pc.empty == 2
    assert pc.non_empty == 1


def test_count_profile_unique_values(monkeypatch):
    _mock_get(monkeypatch, {"A": "x", "B": "x", "C": "y"})
    pc = count_profile("myprofile")
    assert pc.unique_values == 2


def test_count_profile_all_empty(monkeypatch):
    _mock_get(monkeypatch, {"A": "", "B": ""})
    pc = count_profile("myprofile")
    assert pc.empty == 2
    assert pc.non_empty == 0


def test_count_profile_missing_raises(monkeypatch):
    monkeypatch.setattr("envctl.env_count.get_profile", lambda _n: None)
    with pytest.raises(CountError, match="not found"):
        count_profile("ghost")


def test_count_profile_name_preserved(monkeypatch):
    _mock_get(monkeypatch, {"K": "v"})
    pc = count_profile("staging")
    assert pc.name == "staging"


def test_count_profile_total_equals_empty_plus_non_empty(monkeypatch):
    """Sanity check: total must always equal empty + non_empty."""
    _mock_get(monkeypatch, {"A": "1", "B": "", "C": "3", "D": ""})
    pc = count_profile("myprofile")
    assert pc.total == pc.empty + pc.non_empty


# ---------------------------------------------------------------------------
# count_all_profiles
# ---------------------------------------------------------------------------

def test_count_all_profiles_grand_total(monkeypatch):
    _mock_load(monkeypatch, {
        "dev": {"A": "1", "B": ""},
        "prod": {"X": "foo", "Y": "bar", "Z": "baz"},
    })
    summary = count_all_profiles()
    assert summary.grand_total == 5


def test_count_all_profiles_grand_empty(monkeypatch):
    _mock_load(monkeypatch, {
        "dev": {"A": "", "B": ""},
        "prod": {"X": "val"},
    })
    summary = count_all_profiles()
    assert summary.grand_empty == 2
    assert summary.grand_non_empty == 1


def test_count_all_profiles_returns_per_profile_entries(monkeypatch):
    _mock_load(monkeypatch, {
        "alpha": {"K": "v"},
        "beta": {"M": "n", "O": ""},
    })
    summary = count_all_profiles()
    names = [p.name for p in summary.p
