"""Tests for envctl.snapshot."""

from __future__ import annotations

import pytest

from envctl.snapshot import (
    create_snapshot,
    restore_snapshot,
    delete_snapshot,
    list_snapshots,
    SnapshotError,
)
from envctl.storage import load_profiles, save_profiles


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "envctl_store.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.snapshot.get_store_path", lambda: store)
    yield store


def _seed(profiles: dict) -> None:
    save_profiles(profiles)


def test_create_snapshot_captures_profiles():
    _seed({"dev": {"DB": "dev_db"}, "prod": {"DB": "prod_db"}})
    snap = create_snapshot("before-release")
    assert snap["name"] == "before-release"
    assert snap["profiles"]["dev"]["DB"] == "dev_db"
    assert "created_at" in snap


def test_create_snapshot_duplicate_raises():
    _seed({"dev": {"X": "1"}})
    create_snapshot("snap1")
    with pytest.raises(SnapshotError, match="already exists"):
        create_snapshot("snap1")


def test_restore_snapshot_overwrites_profiles():
    _seed({"dev": {"KEY": "original"}})
    create_snapshot("initial")
    _seed({"dev": {"KEY": "changed"}, "staging": {"KEY": "new"}})
    restore_snapshot("initial")
    profiles = load_profiles()
    assert profiles["dev"]["KEY"] == "original"
    assert "staging" not in profiles


def test_restore_snapshot_missing_raises():
    with pytest.raises(SnapshotError, match="not found"):
        restore_snapshot("ghost")


def test_delete_snapshot_removes_entry():
    _seed({"dev": {}})
    create_snapshot("temp")
    delete_snapshot("temp")
    names = [s["name"] for s in list_snapshots()]
    assert "temp" not in names


def test_delete_snapshot_missing_raises():
    with pytest.raises(SnapshotError, match="not found"):
        delete_snapshot("nonexistent")


def test_list_snapshots_newest_first():
    _seed({"dev": {}})
    create_snapshot("alpha")
    create_snapshot("beta")
    create_snapshot("gamma")
    snaps = list_snapshots()
    names = [s["name"] for s in snaps]
    assert names.index("gamma") < names.index("beta") < names.index("alpha")


def test_snapshot_does_not_mutate_on_restore():
    """Restoring a snapshot should not alter the stored snapshot itself."""
    _seed({"dev": {"A": "1"}})
    create_snapshot("frozen")
    _seed({"dev": {"A": "2"}})
    restore_snapshot("frozen")
    snaps = {s["name"]: s for s in list_snapshots()}
    assert snaps["frozen"]["profiles"]["dev"]["A"] == "1"
