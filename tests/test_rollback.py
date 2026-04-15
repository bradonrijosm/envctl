"""Tests for envctl.rollback."""

from __future__ import annotations

import json
import pytest

from envctl.rollback import RollbackError, rollback_to_snapshot, rollback_to_history


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCTL_STORE_DIR", str(tmp_path))
    yield tmp_path


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def _seed_profiles(tmp_path, profiles: dict):
    from envctl.storage import save_profiles
    save_profiles(profiles)


def _seed_snapshot(tmp_path, name: str, profiles: dict):
    snap_path = tmp_path / "snapshots.json"
    existing = json.loads(snap_path.read_text()) if snap_path.exists() else {}
    existing[name] = {"profiles": profiles}
    snap_path.write_text(json.dumps(existing))


def _seed_history(tmp_path, entries: list):
    hist_path = tmp_path / "history.json"
    hist_path.write_text(json.dumps(entries))


# ---------------------------------------------------------------------------
# rollback_to_snapshot
# ---------------------------------------------------------------------------

def test_rollback_snapshot_restores_variables(tmp_path):
    _seed_profiles(tmp_path, {"prod": {"KEY": "new"}})
    _seed_snapshot(tmp_path, "snap1", {"prod": {"KEY": "old", "EXTRA": "val"}})

    result = rollback_to_snapshot("prod", "snap1")
    assert result == {"KEY": "old", "EXTRA": "val"}


def test_rollback_snapshot_persists(tmp_path):
    from envctl.storage import load_profiles
    _seed_profiles(tmp_path, {"prod": {"KEY": "new"}})
    _seed_snapshot(tmp_path, "snap1", {"prod": {"KEY": "old"}})

    rollback_to_snapshot("prod", "snap1")
    assert load_profiles()["prod"]["KEY"] == "old"


def test_rollback_snapshot_missing_snapshot_raises(tmp_path):
    _seed_profiles(tmp_path, {"prod": {}})
    with pytest.raises(RollbackError, match="does not exist"):
        rollback_to_snapshot("prod", "ghost")


def test_rollback_snapshot_profile_not_in_snapshot_raises(tmp_path):
    _seed_profiles(tmp_path, {"prod": {}})
    _seed_snapshot(tmp_path, "snap1", {"staging": {"X": "1"}})
    with pytest.raises(RollbackError, match="was not recorded"):
        rollback_to_snapshot("prod", "snap1")


def test_rollback_snapshot_profile_missing_from_store_raises(tmp_path):
    _seed_profiles(tmp_path, {})
    _seed_snapshot(tmp_path, "snap1", {"prod": {"KEY": "old"}})
    with pytest.raises(RollbackError, match="does not exist in the current store"):
        rollback_to_snapshot("prod", "snap1")


# ---------------------------------------------------------------------------
# rollback_to_history
# ---------------------------------------------------------------------------

def test_rollback_history_restores_one_step(tmp_path):
    _seed_profiles(tmp_path, {"dev": {"KEY": "current"}})
    _seed_history(tmp_path, [
        {"profile": "dev", "variables": {"KEY": "prev1"}},
        {"profile": "dev", "variables": {"KEY": "prev2"}},
    ])
    result = rollback_to_history("dev", steps=1)
    assert result == {"KEY": "prev1"}


def test_rollback_history_restores_two_steps(tmp_path):
    _seed_profiles(tmp_path, {"dev": {"KEY": "current"}})
    _seed_history(tmp_path, [
        {"profile": "dev", "variables": {"KEY": "prev1"}},
        {"profile": "dev", "variables": {"KEY": "prev2"}},
    ])
    result = rollback_to_history("dev", steps=2)
    assert result == {"KEY": "prev2"}


def test_rollback_history_no_entries_raises(tmp_path):
    _seed_profiles(tmp_path, {"dev": {}})
    _seed_history(tmp_path, [])
    with pytest.raises(RollbackError, match="No history entries"):
        rollback_to_history("dev")


def test_rollback_history_steps_exceeds_entries_raises(tmp_path):
    _seed_profiles(tmp_path, {"dev": {}})
    _seed_history(tmp_path, [{"profile": "dev", "variables": {"A": "1"}}])
    with pytest.raises(RollbackError, match="Only 1 history entries"):
        rollback_to_history("dev", steps=5)


def test_rollback_history_invalid_steps_raises(tmp_path):
    _seed_profiles(tmp_path, {"dev": {}})
    with pytest.raises(RollbackError, match="steps must be >= 1"):
        rollback_to_history("dev", steps=0)
