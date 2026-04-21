"""Tests for envctl.env_backup."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from envctl import storage
from envctl.env_backup import BackupError, backup_profile, restore_profile, list_backups


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr(storage, "get_store_path", lambda: str(store))
    return tmp_path


def _seed(name: str, variables: dict) -> None:
    storage.set_profile(name, variables)


# ---------------------------------------------------------------------------
# backup_profile
# ---------------------------------------------------------------------------

def test_backup_creates_file(isolated_store, tmp_path):
    _seed("dev", {"HOST": "localhost", "PORT": "5432"})
    dest = tmp_path / "backups"
    path = backup_profile("dev", str(dest))
    assert Path(path).is_file()


def test_backup_file_contains_variables(isolated_store, tmp_path):
    _seed("dev", {"HOST": "localhost", "PORT": "5432"})
    dest = tmp_path / "backups"
    path = backup_profile("dev", str(dest))
    payload = json.loads(Path(path).read_text())
    assert payload["profile"] == "dev"
    assert payload["variables"] == {"HOST": "localhost", "PORT": "5432"}


def test_backup_with_label_includes_label_in_filename(isolated_store, tmp_path):
    _seed("dev", {"X": "1"})
    dest = tmp_path / "backups"
    path = backup_profile("dev", str(dest), label="pre-release")
    assert "pre-release" in Path(path).name


def test_backup_missing_profile_raises(isolated_store, tmp_path):
    with pytest.raises(BackupError, match="does not exist"):
        backup_profile("ghost", str(tmp_path / "backups"))


# ---------------------------------------------------------------------------
# restore_profile
# ---------------------------------------------------------------------------

def test_restore_profile_success(isolated_store, tmp_path):
    _seed("staging", {"ENV": "staging"})
    dest = tmp_path / "backups"
    path = backup_profile("staging", str(dest))

    # wipe the profile so we can restore it
    storage.set_profile("staging", {})

    name = restore_profile(path, overwrite=True)
    assert name == "staging"
    assert storage.get_profile("staging") == {"ENV": "staging"}


def test_restore_existing_without_overwrite_raises(isolated_store, tmp_path):
    _seed("prod", {"ENV": "prod"})
    dest = tmp_path / "backups"
    path = backup_profile("prod", str(dest))
    with pytest.raises(BackupError, match="already exists"):
        restore_profile(path, overwrite=False)


def test_restore_missing_file_raises(isolated_store, tmp_path):
    with pytest.raises(BackupError, match="not found"):
        restore_profile(str(tmp_path / "no_such_file.json"))


def test_restore_invalid_json_raises(isolated_store, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not-json")
    with pytest.raises(BackupError, match="Invalid backup file"):
        restore_profile(str(bad))


# ---------------------------------------------------------------------------
# list_backups
# ---------------------------------------------------------------------------

def test_list_backups_empty_dir(isolated_store, tmp_path):
    result = list_backups(str(tmp_path / "backups"))
    assert result == []


def test_list_backups_returns_entries(isolated_store, tmp_path):
    _seed("qa", {"ENV": "qa"})
    dest = tmp_path / "backups"
    backup_profile("qa", str(dest))
    backup_profile("qa", str(dest), label="v2")
    entries = list_backups(str(dest))
    assert len(entries) == 2
    assert all(e["profile"] == "qa" for e in entries)
