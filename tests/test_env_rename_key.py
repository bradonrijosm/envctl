"""Tests for envctl.env_rename_key."""

import json
import pytest

from envctl.env_rename_key import RenameKeyError, rename_key, rename_key_all_profiles
from envctl.storage import get_store_path, save_profiles


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.env_rename_key.get_profile",
                        __import__("envctl.storage", fromlist=["get_profile"]).get_profile)
    monkeypatch.setattr("envctl.env_rename_key.set_profile",
                        __import__("envctl.storage", fromlist=["set_profile"]).set_profile)
    monkeypatch.setattr("envctl.env_rename_key.load_profiles",
                        __import__("envctl.storage", fromlist=["load_profiles"]).load_profiles)
    monkeypatch.setattr("envctl.env_rename_key.save_profiles",
                        __import__("envctl.storage", fromlist=["save_profiles"]).save_profiles)
    return store


def _seed(store, profiles: dict):
    store.write_text(json.dumps(profiles))


# ---------------------------------------------------------------------------
# rename_key
# ---------------------------------------------------------------------------

def test_rename_key_success(isolated_store):
    _seed(isolated_store, {"dev": {"HOST": "localhost", "PORT": "5432"}})
    result = rename_key("dev", "HOST", "DB_HOST")
    assert "DB_HOST" in result
    assert "HOST" not in result
    assert result["DB_HOST"] == "localhost"


def test_rename_key_persists_to_store(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    rename_key("dev", "A", "B")
    data = json.loads(isolated_store.read_text())
    assert "B" in data["dev"]
    assert "A" not in data["dev"]


def test_rename_key_missing_profile_raises(isolated_store):
    _seed(isolated_store, {})
    with pytest.raises(RenameKeyError, match="not found"):
        rename_key("ghost", "X", "Y")


def test_rename_key_missing_old_key_raises(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    with pytest.raises(RenameKeyError, match="does not exist"):
        rename_key("dev", "NOPE", "NEW")


def test_rename_key_new_key_exists_no_overwrite_raises(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1", "B": "2"}})
    with pytest.raises(RenameKeyError, match="already exists"):
        rename_key("dev", "A", "B")


def test_rename_key_new_key_exists_with_overwrite(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1", "B": "2"}})
    result = rename_key("dev", "A", "B", overwrite=True)
    assert result["B"] == "1"


# ---------------------------------------------------------------------------
# rename_key_all_profiles
# ---------------------------------------------------------------------------

def test_rename_key_all_profiles_updates_matching(isolated_store):
    _seed(isolated_store, {
        "dev": {"HOST": "dev-host", "PORT": "5432"},
        "prod": {"HOST": "prod-host"},
        "ci": {"TIMEOUT": "30"},
    })
    updated = rename_key_all_profiles("HOST", "DB_HOST")
    assert set(updated.keys()) == {"dev", "prod"}
    assert "ci" not in updated


def test_rename_key_all_profiles_persists(isolated_store):
    _seed(isolated_store, {"dev": {"X": "1"}, "staging": {"X": "2"}})
    rename_key_all_profiles("X", "Y")
    data = json.loads(isolated_store.read_text())
    assert data["dev"]["Y"] == "1"
    assert data["staging"]["Y"] == "2"


def test_rename_key_all_profiles_conflict_raises(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1", "B": "2"}})
    with pytest.raises(RenameKeyError, match="already exists alongside"):
        rename_key_all_profiles("A", "B")


def test_rename_key_all_profiles_no_match_returns_empty(isolated_store):
    _seed(isolated_store, {"dev": {"C": "3"}})
    updated = rename_key_all_profiles("MISSING", "NEW")
    assert updated == {}
