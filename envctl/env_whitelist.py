"""Whitelist support: restrict which keys are allowed in a profile."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envctl.storage import get_store_path, get_profile


class WhitelistError(Exception):
    pass


def _get_whitelist_path() -> Path:
    return get_store_path() / "whitelists.json"


def _load_whitelists() -> Dict[str, List[str]]:
    path = _get_whitelist_path()
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_whitelists(data: Dict[str, List[str]]) -> None:
    path = _get_whitelist_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def set_whitelist(profile: str, keys: List[str]) -> None:
    """Set (replace) the whitelist for *profile*."""
    if get_profile(profile) is None:
        raise WhitelistError(f"Profile '{profile}' does not exist.")
    if not keys:
        raise WhitelistError("Whitelist must contain at least one key.")
    data = _load_whitelists()
    data[profile] = sorted(set(keys))
    _save_whitelists(data)


def get_whitelist(profile: str) -> Optional[List[str]]:
    """Return the whitelist for *profile*, or None if none is set."""
    return _load_whitelists().get(profile)


def remove_whitelist(profile: str) -> None:
    """Remove the whitelist for *profile*."""
    data = _load_whitelists()
    if profile not in data:
        raise WhitelistError(f"No whitelist found for profile '{profile}'.")
    del data[profile]
    _save_whitelists(data)


def check_profile(profile: str) -> List[str]:
    """Return keys in *profile* that are NOT in its whitelist.

    Returns an empty list when no whitelist is set or all keys are allowed.
    """
    whitelist = get_whitelist(profile)
    if whitelist is None:
        return []
    vars_ = get_profile(profile)
    if vars_ is None:
        raise WhitelistError(f"Profile '{profile}' does not exist.")
    allowed = set(whitelist)
    return [k for k in vars_ if k not in allowed]
