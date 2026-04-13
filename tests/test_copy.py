"""Tests for envctl.copy module."""

import pytest

from envctl.copy import CopyError, copy_profile, rename_profile
from envctl.storage import load_profiles, save_profiles


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store_file = tmp_path / "profiles.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store_file)
    yield store_file


def _seed(profiles: dict):
    """Helper to pre-populate the store."""
    save_profiles(profiles)


# ---------------------------------------------------------------------------
# copy_profile
# ---------------------------------------------------------------------------

def test_copy_profile_creates_new_profile():
    _seed({"dev": {"name": "dev", "variables": {"FOO": "bar", "PORT": "8080"}}})
    result = copy_profile("dev", "staging")
    assert result["name"] == "staging"
    assert result["variables"] == {"FOO": "bar", "PORT": "8080"}


def test_copy_profile_persists_to_store():
    _seed({"dev": {"name": "dev", "variables": {"X": "1"}}})
    copy_profile("dev", "prod")
    profiles = load_profiles()
    assert "prod" in profiles
    assert profiles["prod"]["variables"] == {"X": "1"}


def test_copy_profile_original_unchanged():
    _seed({"dev": {"name": "dev", "variables": {"A": "alpha"}}})
    copy_profile("dev", "dev2")
    profiles = load_profiles()
    assert "dev" in profiles
    assert profiles["dev"]["variables"] == {"A": "alpha"}


def test_copy_profile_variables_are_independent():
    """Mutating the copy should not affect the original in-memory dict."""
    _seed({"dev": {"name": "dev", "variables": {"KEY": "val"}}})
    result = copy_profile("dev", "copy")
    result["variables"]["NEW"] = "extra"
    profiles = load_profiles()
    assert "NEW" not in profiles["dev"].get("variables", {})


def test_copy_profile_missing_source_raises():
    _seed({})
    with pytest.raises(CopyError, match="does not exist"):
        copy_profile("ghost", "target")


def test_copy_profile_same_name_raises():
    _seed({"dev": {"name": "dev", "variables": {}}})
    with pytest.raises(CopyError, match="same"):
        copy_profile("dev", "dev")


def test_copy_profile_dest_exists_raises_without_overwrite():
    _seed({
        "dev": {"name": "dev", "variables": {"A": "1"}},
        "prod": {"name": "prod", "variables": {"A": "2"}},
    })
    with pytest.raises(CopyError, match="already exists"):
        copy_profile("dev", "prod")


def test_copy_profile_dest_exists_overwritten_when_flag_set():
    _seed({
        "dev": {"name": "dev", "variables": {"A": "new"}},
        "prod": {"name": "prod", "variables": {"A": "old"}},
    })
    result = copy_profile("dev", "prod", overwrite=True)
    assert result["variables"]["A"] == "new"


# ---------------------------------------------------------------------------
# rename_profile
# ---------------------------------------------------------------------------

def test_rename_profile_creates_new_and_removes_old():
    _seed({"dev": {"name": "dev", "variables": {"ENV": "development"}}})
    rename_profile("dev", "development")
    profiles = load_profiles()
    assert "development" in profiles
    assert "dev" not in profiles


def test_rename_profile_preserves_variables():
    _seed({"alpha": {"name": "alpha", "variables": {"Z": "26"}}})
    result = rename_profile("alpha", "beta")
    assert result["variables"] == {"Z": "26"}
