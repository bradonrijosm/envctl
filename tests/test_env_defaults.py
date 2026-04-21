"""Tests for envctl.env_defaults."""
from __future__ import annotations

import json
import pytest

from envctl.env_defaults import (
    DefaultsError,
    apply_defaults,
    get_default,
    list_defaults,
    remove_default,
    set_default,
    _get_defaults_path,
)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    store.write_text(json.dumps({}))
    monkeypatch.setattr("envctl.env_defaults.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.env_defaults.get_profile", _fake_get_profile)
    monkeypatch.setattr("envctl.env_defaults._get_defaults_path", lambda: tmp_path / "defaults.json")
    yield tmp_path


_PROFILES: dict = {}


def _fake_get_profile(name: str):
    return _PROFILES.get(name)


def _seed(name: str, vars_: dict):
    _PROFILES[name] = vars_


@pytest.fixture(autouse=True)
def reset_profiles():
    _PROFILES.clear()
    yield
    _PROFILES.clear()


def test_set_default_success(isolated_store):
    _seed("dev", {"HOST": "localhost"})
    set_default("dev", "PORT", "8080")
    assert get_default("dev", "PORT") == "8080"


def test_set_default_missing_profile_raises(isolated_store):
    with pytest.raises(DefaultsError, match="does not exist"):
        set_default("ghost", "X", "1")


def test_get_default_no_entry_returns_none(isolated_store):
    _seed("dev", {})
    assert get_default("dev", "MISSING") is None


def test_remove_default_success(isolated_store):
    _seed("dev", {})
    set_default("dev", "PORT", "3000")
    remove_default("dev", "PORT")
    assert get_default("dev", "PORT") is None


def test_remove_default_missing_raises(isolated_store):
    _seed("dev", {})
    with pytest.raises(DefaultsError, match="No default"):
        remove_default("dev", "NOPE")


def test_list_defaults_returns_all(isolated_store):
    _seed("dev", {})
    set_default("dev", "A", "1")
    set_default("dev", "B", "2")
    result = list_defaults("dev")
    assert result == {"A": "1", "B": "2"}


def test_list_defaults_missing_profile_raises(isolated_store):
    with pytest.raises(DefaultsError, match="does not exist"):
        list_defaults("ghost")


def test_apply_defaults_fills_missing_key(isolated_store):
    _seed("dev", {"HOST": "localhost"})
    set_default("dev", "PORT", "9000")
    result = apply_defaults("dev")
    assert result["PORT"] == "9000"
    assert result["HOST"] == "localhost"


def test_apply_defaults_fills_empty_value(isolated_store):
    _seed("dev", {"PORT": ""})
    set_default("dev", "PORT", "8080")
    result = apply_defaults("dev")
    assert result["PORT"] == "8080"


def test_apply_defaults_does_not_overwrite_existing(isolated_store):
    _seed("dev", {"PORT": "3000"})
    set_default("dev", "PORT", "9999")
    result = apply_defaults("dev")
    assert result["PORT"] == "3000"


def test_apply_defaults_missing_profile_raises(isolated_store):
    with pytest.raises(DefaultsError, match="does not exist"):
        apply_defaults("ghost")
