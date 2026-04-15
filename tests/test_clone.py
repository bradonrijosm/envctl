"""Tests for envctl.clone."""

from __future__ import annotations

import json
import pathlib
import pytest

from envctl.clone import CloneError, clone_profile, clone_with_prefix


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    return store


def _seed(isolated_store, profiles: dict) -> None:
    isolated_store.write_text(json.dumps(profiles))


# ---------------------------------------------------------------------------
# clone_profile
# ---------------------------------------------------------------------------

def test_clone_creates_new_profile(isolated_store):
    _seed(isolated_store, {"prod": {"HOST": "prod.example.com", "PORT": "443"}})
    vars_ = clone_profile("prod", "staging")
    assert vars_ == {"HOST": "prod.example.com", "PORT": "443"}


def test_clone_persists_to_store(isolated_store):
    _seed(isolated_store, {"prod": {"HOST": "prod.example.com"}})
    clone_profile("prod", "staging")
    data = json.loads(isolated_store.read_text())
    assert "staging" in data
    assert data["staging"]["HOST"] == "prod.example.com"


def test_clone_original_unchanged(isolated_store):
    _seed(isolated_store, {"prod": {"HOST": "prod.example.com"}})
    clone_profile("prod", "staging")
    data = json.loads(isolated_store.read_text())
    assert data["prod"] == {"HOST": "prod.example.com"}


def test_clone_with_overrides(isolated_store):
    _seed(isolated_store, {"prod": {"HOST": "prod.example.com", "PORT": "443"}})
    vars_ = clone_profile("prod", "staging", overrides={"HOST": "staging.example.com"})
    assert vars_["HOST"] == "staging.example.com"
    assert vars_["PORT"] == "443"


def test_clone_missing_source_raises(isolated_store):
    _seed(isolated_store, {})
    with pytest.raises(CloneError, match="does not exist"):
        clone_profile("ghost", "copy")


def test_clone_dest_exists_raises(isolated_store):
    _seed(isolated_store, {"prod": {"A": "1"}, "staging": {"A": "2"}})
    with pytest.raises(CloneError, match="already exists"):
        clone_profile("prod", "staging")


# ---------------------------------------------------------------------------
# clone_with_prefix
# ---------------------------------------------------------------------------

def test_clone_with_prefix_renames_keys(isolated_store):
    _seed(isolated_store, {"prod": {"HOST": "h", "PORT": "80"}})
    vars_ = clone_with_prefix("prod", "prefixed", "PROD_")
    assert set(vars_.keys()) == {"PROD_HOST", "PROD_PORT"}
    assert vars_["PROD_HOST"] == "h"


def test_clone_with_prefix_persists(isolated_store):
    _seed(isolated_store, {"prod": {"HOST": "h"}})
    clone_with_prefix("prod", "prefixed", "X_")
    data = json.loads(isolated_store.read_text())
    assert "X_HOST" in data["prefixed"]


def test_clone_with_prefix_missing_source_raises(isolated_store):
    _seed(isolated_store, {})
    with pytest.raises(CloneError, match="does not exist"):
        clone_with_prefix("ghost", "copy", "P_")


def test_clone_with_prefix_dest_exists_raises(isolated_store):
    _seed(isolated_store, {"prod": {"A": "1"}, "staging": {"A": "2"}})
    with pytest.raises(CloneError, match="already exists"):
        clone_with_prefix("prod", "staging", "P_")
