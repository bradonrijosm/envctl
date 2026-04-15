"""Tests for envctl.archive."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from envctl.archive import ArchiveError, create_archive, inspect_archive, restore_archive
from envctl.storage import load_profiles, save_profiles


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "store.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.archive.load_profiles",
                        lambda: json.loads(store.read_text()) if store.exists() else {})
    monkeypatch.setattr("envctl.archive.save_profiles",
                        lambda d: store.write_text(json.dumps(d)))
    return tmp_path


def _seed(data: dict):
    from envctl.storage import save_profiles
    save_profiles(data)


def test_create_archive_produces_zip(isolated_store):
    _seed({"dev": {"KEY": "val"}})
    dest = isolated_store / "backup.zip"
    result = create_archive(dest)
    assert result.suffix == ".zip"
    assert result.exists()


def test_create_archive_contains_profiles(isolated_store):
    _seed({"prod": {"DB": "postgres"}})
    dest = isolated_store / "backup.zip"
    create_archive(dest, label="test-label")
    with zipfile.ZipFile(dest) as zf:
        profiles = json.loads(zf.read("profiles.json"))
        manifest = json.loads(zf.read("envctl_manifest.json"))
    assert "prod" in profiles
    assert manifest["label"] == "test-label"
    assert manifest["profile_count"] == 1


def test_create_archive_appends_zip_suffix(isolated_store):
    _seed({})
    dest = isolated_store / "backup"  # no .zip
    result = create_archive(dest)
    assert result.suffix == ".zip"


def test_restore_archive_adds_profiles(isolated_store):
    _seed({"existing": {"X": "1"}})
    dest = isolated_store / "snap.zip"
    with zipfile.ZipFile(dest, "w") as zf:
        zf.writestr("profiles.json", json.dumps({"new_prof": {"Y": "2"}}))
        zf.writestr("envctl_manifest.json", json.dumps({"label": "snap"}))
    restore_archive(dest, overwrite=False)
    from envctl.storage import load_profiles
    profiles = load_profiles()
    assert "existing" in profiles
    assert "new_prof" in profiles


def test_restore_archive_no_overwrite_keeps_existing(isolated_store):
    _seed({"dev": {"KEY": "original"}})
    dest = isolated_store / "snap.zip"
    with zipfile.ZipFile(dest, "w") as zf:
        zf.writestr("profiles.json", json.dumps({"dev": {"KEY": "overwritten"}}))
        zf.writestr("envctl_manifest.json", json.dumps({}))
    restore_archive(dest, overwrite=False)
    from envctl.storage import load_profiles
    assert load_profiles()["dev"]["KEY"] == "original"


def test_restore_archive_overwrite_replaces(isolated_store):
    _seed({"dev": {"KEY": "original"}})
    dest = isolated_store / "snap.zip"
    with zipfile.ZipFile(dest, "w") as zf:
        zf.writestr("profiles.json", json.dumps({"dev": {"KEY": "new"}}))
        zf.writestr("envctl_manifest.json", json.dumps({}))
    restore_archive(dest, overwrite=True)
    from envctl.storage import load_profiles
    assert load_profiles()["dev"]["KEY"] == "new"


def test_restore_archive_missing_file_raises(isolated_store):
    with pytest.raises(ArchiveError, match="not found"):
        restore_archive(isolated_store / "nonexistent.zip")


def test_inspect_archive_returns_profile_names(isolated_store):
    dest = isolated_store / "snap.zip"
    with zipfile.ZipFile(dest, "w") as zf:
        zf.writestr("profiles.json", json.dumps({"a": {}, "b": {}}))
        zf.writestr("envctl_manifest.json", json.dumps({"label": "x"}))
    info = inspect_archive(dest)
    assert set(info["profiles"]) == {"a", "b"}
    assert info["manifest"]["label"] == "x"


def test_inspect_archive_missing_raises(isolated_store):
    with pytest.raises(ArchiveError):
        inspect_archive(isolated_store / "ghost.zip")
