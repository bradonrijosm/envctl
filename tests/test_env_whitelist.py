"""Tests for envctl.env_whitelist."""

from __future__ import annotations

import pytest

from envctl.env_whitelist import (
    WhitelistError,
    check_profile,
    get_whitelist,
    remove_whitelist,
    set_whitelist,
)
from envctl.storage import get_store_path, save_profiles


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.storage.STORE_DIR", tmp_path)
    monkeypatch.setattr("envctl.env_whitelist.get_store_path", lambda: tmp_path)
    return tmp_path


def _seed(isolated_store, profiles):
    save_profiles(profiles)


# ---------------------------------------------------------------------------
# set_whitelist
# ---------------------------------------------------------------------------

def test_set_whitelist_success(isolated_store):
    _seed(isolated_store, {"dev": {"HOST": "localhost", "PORT": "8080"}})
    set_whitelist("dev", ["HOST", "PORT"])
    assert get_whitelist("dev") == ["HOST", "PORT"]


def test_set_whitelist_persists(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    set_whitelist("dev", ["A"])
    # reload from disk
    assert get_whitelist("dev") == ["A"]


def test_set_whitelist_deduplicates_keys(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    set_whitelist("dev", ["A", "A", "B"])
    assert get_whitelist("dev") == ["A", "B"]


def test_set_whitelist_missing_profile_raises(isolated_store):
    _seed(isolated_store, {})
    with pytest.raises(WhitelistError, match="does not exist"):
        set_whitelist("ghost", ["KEY"])


def test_set_whitelist_empty_keys_raises(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    with pytest.raises(WhitelistError, match="at least one key"):
        set_whitelist("dev", [])


# ---------------------------------------------------------------------------
# get_whitelist
# ---------------------------------------------------------------------------

def test_get_whitelist_returns_none_when_unset(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    assert get_whitelist("dev") is None


# ---------------------------------------------------------------------------
# remove_whitelist
# ---------------------------------------------------------------------------

def test_remove_whitelist_success(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    set_whitelist("dev", ["A"])
    remove_whitelist("dev")
    assert get_whitelist("dev") is None


def test_remove_whitelist_missing_raises(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    with pytest.raises(WhitelistError, match="No whitelist found"):
        remove_whitelist("dev")


# ---------------------------------------------------------------------------
# check_profile
# ---------------------------------------------------------------------------

def test_check_profile_no_whitelist_returns_empty(isolated_store):
    _seed(isolated_store, {"dev": {"HOST": "localhost"}})
    assert check_profile("dev") == []


def test_check_profile_all_allowed_returns_empty(isolated_store):
    _seed(isolated_store, {"dev": {"HOST": "localhost", "PORT": "8080"}})
    set_whitelist("dev", ["HOST", "PORT"])
    assert check_profile("dev") == []


def test_check_profile_detects_disallowed_keys(isolated_store):
    _seed(isolated_store, {"dev": {"HOST": "localhost", "SECRET": "abc"}})
    set_whitelist("dev", ["HOST"])
    violations = check_profile("dev")
    assert "SECRET" in violations
    assert "HOST" not in violations
