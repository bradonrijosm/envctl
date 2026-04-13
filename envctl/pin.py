"""Profile pinning — mark a profile as the default/active one for a project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envctl.storage import get_store_path, load_profiles

_PINS_FILE = "pins.json"


class PinError(Exception):
    """Raised when a pin operation fails."""


def _get_pins_path() -> Path:
    return get_store_path() / _PINS_FILE


def _load_pins() -> dict[str, str]:
    path = _get_pins_path()
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_pins(pins: dict[str, str]) -> None:
    path = _get_pins_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(pins, fh, indent=2)


def pin_profile(project: str, profile_name: str) -> None:
    """Pin *profile_name* as the active profile for *project*."""
    profiles = load_profiles()
    if profile_name not in profiles:
        raise PinError(f"Profile '{profile_name}' does not exist.")
    pins = _load_pins()
    pins[project] = profile_name
    _save_pins(pins)


def unpin_profile(project: str) -> None:
    """Remove the pinned profile for *project*."""
    pins = _load_pins()
    if project not in pins:
        raise PinError(f"No pinned profile found for project '{project}'.")
    del pins[project]
    _save_pins(pins)


def get_pinned(project: str) -> Optional[str]:
    """Return the pinned profile name for *project*, or None if not set."""
    return _load_pins().get(project)


def list_pins() -> dict[str, str]:
    """Return a mapping of project -> pinned profile name."""
    return dict(_load_pins())
