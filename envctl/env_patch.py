"""Patch a profile by applying a dict of changes (set/unset operations)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envctl.storage import get_profile, set_profile


class PatchError(Exception):
    """Raised when a patch operation fails."""


@dataclass
class PatchResult:
    profile: str
    set_keys: List[str] = field(default_factory=list)
    unset_keys: List[str] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return len(self.set_keys) + len(self.unset_keys)


def patch_profile(
    profile_name: str,
    set_vars: Optional[Dict[str, str]] = None,
    unset_vars: Optional[List[str]] = None,
    create_missing: bool = False,
) -> PatchResult:
    """Apply a patch to a named profile.

    Args:
        profile_name: Target profile name.
        set_vars: Mapping of keys to new values to set.
        unset_vars: List of keys to remove from the profile.
        create_missing: If True, allow setting keys not already present.
                        If False, skip keys that don't exist when setting.

    Returns:
        A PatchResult describing what changed.

    Raises:
        PatchError: If the profile does not exist.
    """
    existing = get_profile(profile_name)
    if existing is None:
        raise PatchError(f"Profile '{profile_name}' not found.")

    result = PatchResult(profile=profile_name)
    updated = dict(existing)

    for key, value in (set_vars or {}).items():
        if not create_missing and key not in updated:
            result.skipped_keys.append(key)
            continue
        updated[key] = value
        result.set_keys.append(key)

    for key in unset_vars or []:
        if key in updated:
            del updated[key]
            result.unset_keys.append(key)
        else:
            result.skipped_keys.append(key)

    if result.total_changes > 0:
        set_profile(profile_name, updated)

    return result
