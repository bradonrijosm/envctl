"""envctl.env_defaults — manage default values for profile variables.

Allows setting a fallback value for a variable that is used when the
variable is missing or empty in a given profile.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envctl.storage import get_store_path, get_profile


class DefaultsError(Exception):
    """Raised when a defaults operation fails."""


def _get_defaults_path() -> Path:
    return get_store_path().parent / "defaults.json"


def _load_defaults() -> Dict[str, Dict[str, str]]:
    """Return mapping of profile -> {var: default_value}."""
    path = _get_defaults_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_defaults(data: Dict[str, Dict[str, str]]) -> None:
    _get_defaults_path().write_text(json.dumps(data, indent=2))


def set_default(profile: str, key: str, value: str) -> None:
    """Register *value* as the default for *key* in *profile*."""
    if get_profile(profile) is None:
        raise DefaultsError(f"Profile '{profile}' does not exist.")
    data = _load_defaults()
    data.setdefault(profile, {})[key] = value
    _save_defaults(data)


def remove_default(profile: str, key: str) -> None:
    """Remove the default for *key* in *profile*."""
    data = _load_defaults()
    if profile not in data or key not in data[profile]:
        raise DefaultsError(f"No default for '{key}' in profile '{profile}'.")
    del data[profile][key]
    if not data[profile]:
        del data[profile]
    _save_defaults(data)


def get_default(profile: str, key: str) -> Optional[str]:
    """Return the registered default for *key* in *profile*, or None."""
    return _load_defaults().get(profile, {}).get(key)


def list_defaults(profile: str) -> Dict[str, str]:
    """Return all defaults registered for *profile*."""
    if get_profile(profile) is None:
        raise DefaultsError(f"Profile '{profile}' does not exist.")
    return dict(_load_defaults().get(profile, {}))


def apply_defaults(profile: str) -> Dict[str, str]:
    """Return profile variables with defaults filled in for missing/empty keys."""
    vars_ = get_profile(profile)
    if vars_ is None:
        raise DefaultsError(f"Profile '{profile}' does not exist.")
    defaults = _load_defaults().get(profile, {})
    result = dict(vars_)
    for key, default_val in defaults.items():
        if not result.get(key):  # missing or empty string
            result[key] = default_val
    return result
