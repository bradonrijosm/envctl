"""Tests for envctl.storage module."""

import json
import os
from pathlib import Path

import pytest

import envctl.storage as storage


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    """Redirect ENVCTL_HOME to a temporary directory for each test."""
    monkeypatch.setenv("ENVCTL_HOME", str(tmp_path))
    yield tmp_path


def test_load_profiles_empty():
    assert storage.load_profiles() == {}


def test_save_and_load_profiles():
    profiles = {"dev": {"DEBUG": "true", "PORT": "8000"}}
    storage.save_profiles(profiles)
    assert storage.load_profiles() == profiles


def test_set_and_get_profile():
    storage.set_profile("prod", {"ENV": "production"})
    assert storage.get_profile("prod") == {"ENV": "production"}


def test_get_profile_missing_returns_none():
    assert storage.get_profile("nonexistent") is None


def test_delete_profile_existing():
    storage.set_profile("staging", {"ENV": "staging"})
    result = storage.delete_profile("staging")
    assert result is True
    assert storage.get_profile("staging") is None


def test_delete_profile_missing_returns_false():
    assert storage.delete_profile("ghost") is False


def test_list_profile_names_sorted():
    storage.set_profile("zebra", {})
    storage.set_profile("alpha", {})
    storage.set_profile("middle", {})
    assert storage.list_profile_names() == ["alpha", "middle", "zebra"]


def test_profiles_file_is_valid_json(isolated_store):
    storage.set_profile("test", {"KEY": "val"})
    profiles_file = isolated_store / storage.PROFILES_FILE
    data = json.loads(profiles_file.read_text())
    assert "test" in data


def test_set_profile_overwrites_existing():
    """Setting a profile that already exists should replace its variables."""
    storage.set_profile("dev", {"DEBUG": "true", "PORT": "8000"})
    storage.set_profile("dev", {"DEBUG": "false"})
    assert storage.get_profile("dev") == {"DEBUG": "false"}


def test_list_profile_names_empty():
    """list_profile_names should return an empty list when no profiles exist."""
    assert storage.list_profile_names() == []
