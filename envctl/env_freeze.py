"""Freeze and unfreeze profile variables — frozen profiles cannot be modified."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envctl.storage import get_store_path, get_profile


class FreezeError(Exception):
    """Raised when a freeze operation fails."""


def _get_freeze_path() -> Path:
    return get_store_path().parent / "freeze.json"


def _load_frozen() -> Dict[str, List[str]]:
    """Return mapping of profile_name -> list of frozen keys (or ["*"] for all)."""
    p = _get_freeze_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_frozen(data: Dict[str, List[str]]) -> None:
    _get_freeze_path().write_text(json.dumps(data, indent=2))


def freeze_profile(profile: str, keys: List[str] | None = None) -> None:
    """Freeze all keys (or specific keys) in a profile.

    If *keys* is None or empty, the entire profile is frozen (represented as ["*"]).
    """
    if get_profile(profile) is None:
        raise FreezeError(f"Profile '{profile}' does not exist.")
    frozen = _load_frozen()
    if keys:
        existing = set(frozen.get(profile, []))
        if "*" in existing:
            raise FreezeError(f"Profile '{profile}' is already fully frozen.")
        existing.update(keys)
        frozen[profile] = sorted(existing)
    else:
        frozen[profile] = ["*"]
    _save_frozen(frozen)


def unfreeze_profile(profile: str, keys: List[str] | None = None) -> None:
    """Unfreeze all keys (or specific keys) in a profile."""
    frozen = _load_frozen()
    if profile not in frozen:
        raise FreezeError(f"Profile '{profile}' is not frozen.")
    if keys:
        current = set(frozen.get(profile, []))
        if "*" in current:
            raise FreezeError(
                f"Profile '{profile}' is fully frozen; unfreeze entirely first."
            )
        current -= set(keys)
        if current:
            frozen[profile] = sorted(current)
        else:
            del frozen[profile]
    else:
        del frozen[profile]
    _save_frozen(frozen)


def is_frozen(profile: str, key: str | None = None) -> bool:
    """Return True if the profile (or a specific key within it) is frozen."""
    frozen = _load_frozen()
    entry = frozen.get(profile)
    if entry is None:
        return False
    if "*" in entry:
        return True
    if key is not None:
        return key in entry
    return bool(entry)


def list_frozen() -> Dict[str, List[str]]:
    """Return all frozen profiles and their frozen keys."""
    return _load_frozen()


def assert_not_frozen(profile: str, key: str | None = None) -> None:
    """Raise FreezeError if the profile or key is frozen."""
    if is_frozen(profile, key):
        target = f"key '{key}' in profile '{profile}'" if key else f"profile '{profile}'"
        raise FreezeError(f"Cannot modify {target}: it is frozen.")
