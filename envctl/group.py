"""Group management: organize profiles into named groups."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envctl.storage import get_store_path, load_profiles


class GroupError(Exception):
    """Raised when a group operation fails."""


def _get_group_path() -> Path:
    return get_store_path().parent / "groups.json"


def _load_groups() -> Dict[str, List[str]]:
    path = _get_group_path()
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_groups(groups: Dict[str, List[str]]) -> None:
    path = _get_group_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(groups, fh, indent=2)


def create_group(name: str) -> None:
    """Create an empty group."""
    groups = _load_groups()
    if name in groups:
        raise GroupError(f"Group '{name}' already exists.")
    groups[name] = []
    _save_groups(groups)


def delete_group(name: str) -> None:
    """Delete a group (does not delete member profiles)."""
    groups = _load_groups()
    if name not in groups:
        raise GroupError(f"Group '{name}' does not exist.")
    del groups[name]
    _save_groups(groups)


def add_profile_to_group(group: str, profile: str) -> None:
    """Add a profile to a group."""
    profiles = load_profiles()
    if profile not in profiles:
        raise GroupError(f"Profile '{profile}' does not exist.")
    groups = _load_groups()
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    if profile in groups[group]:
        raise GroupError(f"Profile '{profile}' is already in group '{group}'.")
    groups[group].append(profile)
    _save_groups(groups)


def remove_profile_from_group(group: str, profile: str) -> None:
    """Remove a profile from a group."""
    groups = _load_groups()
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    if profile not in groups[group]:
        raise GroupError(f"Profile '{profile}' is not in group '{group}'.")
    groups[group].remove(profile)
    _save_groups(groups)


def list_groups() -> Dict[str, List[str]]:
    """Return all groups and their members."""
    return _load_groups()


def get_group_members(group: str) -> List[str]:
    """Return the list of profile names in a group."""
    groups = _load_groups()
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    return list(groups[group])
