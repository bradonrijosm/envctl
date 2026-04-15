"""Watch a profile for changes and emit shell reload hints."""

from __future__ import annotations

import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Callable, Optional

from envctl.storage import get_store_path, load_profiles


class WatchError(Exception):
    """Raised when a watch operation fails."""


@dataclass
class WatchState:
    profile_name: str
    last_hash: str = ""
    change_count: int = 0
    callbacks: list[Callable[[str, dict, dict], None]] = field(default_factory=list)


def _hash_profile(variables: dict) -> str:
    """Return a stable hash for a variable dict."""
    serialized = json.dumps(variables, sort_keys=True).encode()
    return hashlib.sha256(serialized).hexdigest()


def _current_variables(profile_name: str) -> Optional[dict]:
    """Load current variables for a profile, or None if missing."""
    profiles = load_profiles()
    return profiles.get(profile_name)


def watch_profile(
    profile_name: str,
    on_change: Callable[[str, dict, dict], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll the store and invoke *on_change(profile, old_vars, new_vars)* on change.

    Runs until *max_iterations* is reached (useful for testing) or KeyboardInterrupt.
    """
    variables = _current_variables(profile_name)
    if variables is None:
        raise WatchError(f"Profile '{profile_name}' does not exist.")

    current_hash = _hash_profile(variables)
    iterations = 0

    try:
        while max_iterations is None or iterations < max_iterations:
            time.sleep(interval)
            new_vars = _current_variables(profile_name)
            if new_vars is None:
                raise WatchError(f"Profile '{profile_name}' was removed during watch.")
            new_hash = _hash_profile(new_vars)
            if new_hash != current_hash:
                on_change(profile_name, dict(variables), dict(new_vars))
                variables = new_vars
                current_hash = new_hash
            iterations += 1
    except KeyboardInterrupt:
        pass
