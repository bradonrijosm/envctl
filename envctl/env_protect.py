"""Protection rules for individual environment variable keys within a profile."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envctl.storage import get_store_path, get_profile


class ProtectError(Exception):
    """Raised when a protection operation fails."""


def _get_protect_path() -> Path:
    return get_store_path() / "protected_keys.json"


def _load_protected() -> Dict[str, List[str]]:
    path = _get_protect_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_protected(data: Dict[str, List[str]]) -> None:
    _get_protect_path().write_text(json.dumps(data, indent=2))


def protect_key(profile: str, key: str) -> None:
    """Mark *key* in *profile* as protected (cannot be overwritten or deleted)."""
    if get_profile(profile) is None:
        raise ProtectError(f"Profile '{profile}' does not exist.")
    data = _load_protected()
    keys: List[str] = data.setdefault(profile, [])
    if key in keys:
        raise ProtectError(f"Key '{key}' is already protected in profile '{profile}'.")
    keys.append(key)
    _save_protected(data)


def unprotect_key(profile: str, key: str) -> None:
    """Remove protection from *key* in *profile*."""
    data = _load_protected()
    keys: List[str] = data.get(profile, [])
    if key not in keys:
        raise ProtectError(f"Key '{key}' is not protected in profile '{profile}'.")
    keys.remove(key)
    if not keys:
        del data[profile]
    _save_protected(data)


def list_protected(profile: str) -> List[str]:
    """Return the list of protected keys for *profile* (sorted)."""
    data = _load_protected()
    return sorted(data.get(profile, []))


def is_protected(profile: str, key: str) -> bool:
    """Return True if *key* is protected in *profile*."""
    return key in _load_protected().get(profile, [])


def assert_not_protected(profile: str, key: str) -> None:
    """Raise ProtectError if *key* is protected in *profile*."""
    if is_protected(profile, key):
        raise ProtectError(
            f"Key '{key}' is protected in profile '{profile}' and cannot be modified."
        )
