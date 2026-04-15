"""Snapshot support: save and restore full profile-set states."""

from __future__ import annotations

import copy
import datetime
from typing import Dict, List, Optional

from envctl.storage import load_profiles, save_profiles, get_store_path

_SNAPSHOT_KEY = "__snapshots__"


class SnapshotError(Exception):
    """Raised when a snapshot operation fails."""


def _load_snapshots() -> Dict[str, dict]:
    """Return the snapshots sub-dict from the store file."""
    import json
    path = get_store_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        return data.get(_SNAPSHOT_KEY, {})
    except (json.JSONDecodeError, OSError):
        return {}


def _save_snapshots(snapshots: Dict[str, dict]) -> None:
    """Persist snapshots into the store file alongside profiles."""
    import json
    path = get_store_path()
    try:
        data = json.loads(path.read_text()) if path.exists() else {}
    except (json.JSONDecodeError, OSError):
        data = {}
    data[_SNAPSHOT_KEY] = snapshots
    path.write_text(json.dumps(data, indent=2))


def create_snapshot(name: str) -> dict:
    """Capture the current profiles state under *name*."""
    snapshots = _load_snapshots()
    if name in snapshots:
        raise SnapshotError(f"Snapshot '{name}' already exists.")
    profiles = load_profiles()
    entry = {
        "name": name,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "profiles": copy.deepcopy(profiles),
    }
    snapshots[name] = entry
    _save_snapshots(snapshots)
    return entry


def restore_snapshot(name: str) -> None:
    """Overwrite current profiles with those stored in *name*."""
    snapshots = _load_snapshots()
    if name not in snapshots:
        raise SnapshotError(f"Snapshot '{name}' not found.")
    save_profiles(copy.deepcopy(snapshots[name]["profiles"]))


def delete_snapshot(name: str) -> None:
    """Remove a snapshot by name."""
    snapshots = _load_snapshots()
    if name not in snapshots:
        raise SnapshotError(f"Snapshot '{name}' not found.")
    del snapshots[name]
    _save_snapshots(snapshots)


def list_snapshots() -> List[dict]:
    """Return all snapshots sorted newest-first."""
    snapshots = _load_snapshots()
    return sorted(snapshots.values(), key=lambda s: s["created_at"], reverse=True)


def rename_snapshot(old_name: str, new_name: str) -> None:
    """Rename an existing snapshot from *old_name* to *new_name*.

    Raises SnapshotError if *old_name* does not exist or *new_name* is
    already taken.
    """
    snapshots = _load_snapshots()
    if old_name not in snapshots:
        raise SnapshotError(f"Snapshot '{old_name}' not found.")
    if new_name in snapshots:
        raise SnapshotError(f"Snapshot '{new_name}' already exists.")
    entry = snapshots.pop(old_name)
    entry["name"] = new_name
    snapshots[new_name] = entry
    _save_snapshots(snapshots)
