"""Tests for envctl.env_patch."""

from __future__ import annotations

import json
import os
import pytest

from envctl.env_patch import PatchError, PatchResult, patch_profile


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setenv("ENVCTL_STORE", str(store))
    return store


def _seed(isolated_store, profiles: dict):
    isolated_store.write_text(json.dumps(profiles))


# ---------------------------------------------------------------------------
# patch_profile — set_vars
# ---------------------------------------------------------------------------

def test_patch_set_existing_key(isolated_store):
    _seed(isolated_store, {"dev": {"HOST": "localhost", "PORT": "8080"}})
    result = patch_profile("dev", set_vars={"PORT": "9090"})
    assert "PORT" in result.set_keys
    data = json.loads(isolated_store.read_text())
    assert data["dev"]["PORT"] == "9090"


def test_patch_set_new_key_with_create_missing(isolated_store):
    _seed(isolated_store, {"dev": {"HOST": "localhost"}})
    result = patch_profile("dev", set_vars={"NEW_KEY": "value"}, create_missing=True)
    assert "NEW_KEY" in result.set_keys
    data = json.loads(isolated_store.read_text())
    assert data["dev"]["NEW_KEY"] == "value"


def test_patch_set_new_key_without_create_missing_skips(isolated_store):
    _seed(isolated_store, {"dev": {"HOST": "localhost"}})
    result = patch_profile("dev", set_vars={"GHOST": "value"}, create_missing=False)
    assert "GHOST" in result.skipped_keys
    assert "GHOST" not in result.set_keys
    data = json.loads(isolated_store.read_text())
    assert "GHOST" not in data["dev"]


# ---------------------------------------------------------------------------
# patch_profile — unset_vars
# ---------------------------------------------------------------------------

def test_patch_unset_existing_key(isolated_store):
    _seed(isolated_store, {"dev": {"HOST": "localhost", "PORT": "8080"}})
    result = patch_profile("dev", unset_vars=["PORT"])
    assert "PORT" in result.unset_keys
    data = json.loads(isolated_store.read_text())
    assert "PORT" not in data["dev"]


def test_patch_unset_missing_key_is_skipped(isolated_store):
    _seed(isolated_store, {"dev": {"HOST": "localhost"}})
    result = patch_profile("dev", unset_vars=["MISSING"])
    assert "MISSING" in result.skipped_keys
    assert result.total_changes == 0


# ---------------------------------------------------------------------------
# patch_profile — combined
# ---------------------------------------------------------------------------

def test_patch_set_and_unset_together(isolated_store):
    _seed(isolated_store, {"dev": {"HOST": "localhost", "PORT": "8080"}})
    result = patch_profile("dev", set_vars={"HOST": "prod.example.com"}, unset_vars=["PORT"])
    assert "HOST" in result.set_keys
    assert "PORT" in result.unset_keys
    assert result.total_changes == 2
    data = json.loads(isolated_store.read_text())
    assert data["dev"]["HOST"] == "prod.example.com"
    assert "PORT" not in data["dev"]


def test_patch_no_changes_does_not_rewrite(isolated_store):
    _seed(isolated_store, {"dev": {"HOST": "localhost"}})
    mtime_before = isolated_store.stat().st_mtime
    result = patch_profile("dev", set_vars={}, unset_vars=[])
    assert result.total_changes == 0
    # File should not have been touched
    assert isolated_store.stat().st_mtime == mtime_before


# ---------------------------------------------------------------------------
# patch_profile — error handling
# ---------------------------------------------------------------------------

def test_patch_missing_profile_raises(isolated_store):
    _seed(isolated_store, {})
    with pytest.raises(PatchError, match="not found"):
        patch_profile("nonexistent", set_vars={"X": "1"})
