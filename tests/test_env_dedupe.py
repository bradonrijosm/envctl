"""Tests for envctl.env_dedupe."""

from __future__ import annotations

import json
import pathlib

import pytest

from envctl.env_dedupe import DedupeError, DedupeResult, dedupe_profile, find_duplicates


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    return store


def _seed(store: pathlib.Path, profiles: dict) -> None:
    store.write_text(json.dumps(profiles))


# ---------------------------------------------------------------------------
# find_duplicates
# ---------------------------------------------------------------------------


def test_find_duplicates_no_dupes(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1", "B": "2", "C": "3"}})
    result = find_duplicates("dev")
    assert not result.has_duplicates
    assert result.duplicates == {}


def test_find_duplicates_detects_shared_values(isolated_store):
    _seed(isolated_store, {"dev": {"A": "same", "B": "same", "C": "other"}})
    result = find_duplicates("dev")
    assert result.has_duplicates
    assert set(result.duplicates["same"]) == {"A", "B"}


def test_find_duplicates_missing_profile_raises(isolated_store):
    _seed(isolated_store, {})
    with pytest.raises(DedupeError, match="does not exist"):
        find_duplicates("ghost")


# ---------------------------------------------------------------------------
# dedupe_profile — keep="first"
# ---------------------------------------------------------------------------


def test_dedupe_removes_duplicate_keeps_first(isolated_store):
    _seed(isolated_store, {"dev": {"A": "dup", "B": "dup", "C": "unique"}})
    result = dedupe_profile("dev", keep="first")
    # Lexicographically first key is "A"; "B" should be removed
    assert "B" in result.removed_keys
    assert "A" not in result.removed_keys


def test_dedupe_keeps_last(isolated_store):
    _seed(isolated_store, {"dev": {"A": "dup", "B": "dup", "C": "unique"}})
    result = dedupe_profile("dev", keep="last")
    assert "A" in result.removed_keys
    assert "B" not in result.removed_keys


def test_dedupe_persists_changes(isolated_store):
    _seed(isolated_store, {"dev": {"X": "v", "Y": "v", "Z": "other"}})
    dedupe_profile("dev", keep="first")
    data = json.loads(isolated_store.read_text())
    assert "Y" not in data["dev"]
    assert "X" in data["dev"]


def test_dedupe_dry_run_does_not_modify(isolated_store):
    original = {"dev": {"X": "v", "Y": "v"}}
    _seed(isolated_store, original)
    result = dedupe_profile("dev", dry_run=True)
    assert result.removed_keys  # would remove something
    data = json.loads(isolated_store.read_text())
    assert data == original  # unchanged


def test_dedupe_no_duplicates_returns_empty_removed(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1", "B": "2"}})
    result = dedupe_profile("dev")
    assert result.removed_keys == []


def test_dedupe_invalid_keep_raises(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    with pytest.raises(DedupeError, match="Invalid keep strategy"):
        dedupe_profile("dev", keep="middle")


def test_dedupe_missing_profile_raises(isolated_store):
    _seed(isolated_store, {})
    with pytest.raises(DedupeError, match="does not exist"):
        dedupe_profile("nope")
