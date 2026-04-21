"""Tests for envctl.env_flatten."""

from __future__ import annotations

import json
import pytest

from envctl.env_flatten import FlattenError, flatten_profile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_profiles(tmp_path, profiles: dict):
    store = tmp_path / "profiles.json"
    store.write_text(json.dumps(profiles))
    return store


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    """Redirect storage to a temporary directory."""
    monkeypatch.setattr(
        "envctl.storage.get_store_path", lambda: tmp_path / "profiles.json"
    )
    monkeypatch.setattr(
        "envctl.env_flatten.load_profiles",
        lambda: json.loads((tmp_path / "profiles.json").read_text())
        if (tmp_path / "profiles.json").exists()
        else {},
    )
    return tmp_path


def _seed(tmp_path, profiles: dict):
    (tmp_path / "profiles.json").write_text(json.dumps(profiles))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_flatten_simple_no_references(isolated_store):
    _seed(isolated_store, {"dev": {"HOST": "localhost", "PORT": "5432"}})
    result = flatten_profile("dev")
    assert result == {"HOST": "localhost", "PORT": "5432"}


def test_flatten_resolves_self_reference(isolated_store):
    _seed(
        isolated_store,
        {"dev": {"BASE": "postgres", "URL": "${BASE}://localhost"}},
    )
    result = flatten_profile("dev")
    assert result["URL"] == "postgres://localhost"


def test_flatten_missing_profile_raises(isolated_store):
    _seed(isolated_store, {})
    with pytest.raises(FlattenError, match="does not exist"):
        flatten_profile("ghost")


def test_flatten_missing_var_reference_raises(isolated_store):
    _seed(isolated_store, {"dev": {"URL": "${UNDEFINED}://host"}})
    with pytest.raises(FlattenError, match="not found during flattening"):
        flatten_profile("dev")


def test_flatten_with_base_profile_merges(isolated_store):
    _seed(
        isolated_store,
        {
            "base": {"HOST": "localhost", "PORT": "5432"},
            "prod": {"HOST": "prod.db.example.com"},
        },
    )
    result = flatten_profile("prod", base_profile="base")
    assert result["HOST"] == "prod.db.example.com"
    assert result["PORT"] == "5432"


def test_flatten_base_profile_missing_raises(isolated_store):
    _seed(isolated_store, {"dev": {"X": "1"}})
    with pytest.raises(FlattenError, match="Base profile 'nonexistent' does not exist"):
        flatten_profile("dev", base_profile="nonexistent")


def test_flatten_cross_var_chain(isolated_store):
    _seed(
        isolated_store,
        {"dev": {"A": "hello", "B": "${A}_world", "C": "${B}!"}},
    )
    result = flatten_profile("dev")
    assert result["C"] == "hello_world!"
