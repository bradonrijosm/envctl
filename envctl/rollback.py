"""Rollback support: revert a profile to a previous snapshot or history entry."""

from __future__ import annotations

from typing import Optional

from envctl.storage import load_profiles, save_profiles
from envctl.snapshot import _load_snapshots
from envctl.history import _load_history


class RollbackError(Exception):
    """Raised when a rollback operation fails."""


def rollback_to_snapshot(profile_name: str, snapshot_name: str) -> dict:
    """Restore a single profile's variables from a named snapshot.

    Returns the restored variables dict.
    Raises RollbackError if the snapshot or profile within it is not found.
    """
    snapshots = _load_snapshots()
    if snapshot_name not in snapshots:
        raise RollbackError(f"Snapshot '{snapshot_name}' does not exist.")

    snap_profiles = snapshots[snapshot_name].get("profiles", {})
    if profile_name not in snap_profiles:
        raise RollbackError(
            f"Profile '{profile_name}' was not recorded in snapshot '{snapshot_name}'."
        )

    restored_vars = dict(snap_profiles[profile_name])

    all_profiles = load_profiles()
    if profile_name not in all_profiles:
        raise RollbackError(
            f"Profile '{profile_name}' does not exist in the current store."
        )

    all_profiles[profile_name] = restored_vars
    save_profiles(all_profiles)
    return restored_vars


def rollback_to_history(profile_name: str, steps: int = 1) -> Optional[dict]:
    """Revert a profile's variables to a state recorded *steps* activations ago.

    History entries store the variables at activation time.
    Returns the restored variables dict, or raises RollbackError.
    """
    if steps < 1:
        raise RollbackError("steps must be >= 1.")

    history = _load_history()
    profile_entries = [
        e for e in history if e.get("profile") == profile_name and "variables" in e
    ]

    if not profile_entries:
        raise RollbackError(
            f"No history entries with variables found for profile '{profile_name}'."
        )

    if steps > len(profile_entries):
        raise RollbackError(
            f"Only {len(profile_entries)} history entries available for '{profile_name}'; "
            f"cannot roll back {steps} steps."
        )

    target_entry = profile_entries[steps - 1]
    restored_vars = dict(target_entry["variables"])

    all_profiles = load_profiles()
    if profile_name not in all_profiles:
        raise RollbackError(
            f"Profile '{profile_name}' does not exist in the current store."
        )

    all_profiles[profile_name] = restored_vars
    save_profiles(all_profiles)
    return restored_vars
