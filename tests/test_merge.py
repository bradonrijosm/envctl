"""Tests for envctl.merge."""

import pytest
from pathlib import Path
from envctl.merge import merge_profiles, MergeError
from envctl.storage import save_profiles, load_profiles


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    yield store


def _seed(data: dict):
    """Persist a profiles dict directly."""
    save_profiles(data)


def test_merge_adds_missing_keys():
    _seed({
        "base": {"variables": {"HOST": "localhost", "PORT": "5432"}},
        "dev":  {"variables": {"DEBUG": "true"}},
    })
    result = merge_profiles("base", "dev")
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"
    assert result["DEBUG"] == "true"


def test_merge_no_overwrite_keeps_target_values():
    _seed({
        "base": {"variables": {"HOST": "prod-host", "PORT": "5432"}},
        "dev":  {"variables": {"HOST": "localhost"}},
    })
    result = merge_profiles("base", "dev", overwrite=False)
    assert result["HOST"] == "localhost"  # target wins
    assert result["PORT"] == "5432"


def test_merge_overwrite_replaces_target_values():
    _seed({
        "base": {"variables": {"HOST": "prod-host", "PORT": "5432"}},
        "dev":  {"variables": {"HOST": "localhost"}},
    })
    result = merge_profiles("base", "dev", overwrite=True)
    assert result["HOST"] == "prod-host"  # source wins


def test_merge_persists_to_store():
    _seed({
        "base": {"variables": {"NEW_KEY": "value"}},
        "dev":  {"variables": {}},
    })
    merge_profiles("base", "dev")
    profiles = load_profiles()
    assert profiles["dev"]["variables"]["NEW_KEY"] == "value"


def test_merge_missing_source_raises():
    _seed({"dev": {"variables": {}}})
    with pytest.raises(MergeError, match="Source profile"):
        merge_profiles("nonexistent", "dev")


def test_merge_missing_target_raises():
    _seed({"base": {"variables": {}}})
    with pytest.raises(MergeError, match="Target profile"):
        merge_profiles("base", "nonexistent")


def test_merge_same_profile_raises():
    _seed({"base": {"variables": {"X": "1"}}})
    with pytest.raises(MergeError, match="different"):
        merge_profiles("base", "base")
