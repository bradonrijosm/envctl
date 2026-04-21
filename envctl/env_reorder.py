"""Reorder environment variable keys within a profile."""

from __future__ import annotations

from typing import List

from envctl.storage import get_profile, set_profile


class ReorderError(Exception):
    """Raised when a reorder operation fails."""


def reorder_keys(profile: str, order: List[str], *, fill_remaining: bool = True) -> dict:
    """Return a new variable dict with keys reordered according to *order*.

    Keys listed in *order* appear first (in that sequence).  If
    *fill_remaining* is True, any keys not mentioned in *order* are appended
    afterwards in their original relative order.  If False, unlisted keys are
    dropped from the result.

    Raises ReorderError if the profile does not exist or if *order* contains
    a key that is not present in the profile.
    """
    vars_ = get_profile(profile)
    if vars_ is None:
        raise ReorderError(f"Profile '{profile}' does not exist.")

    unknown = [k for k in order if k not in vars_]
    if unknown:
        raise ReorderError(
            f"Keys not found in profile '{profile}': {', '.join(unknown)}"
        )

    reordered: dict = {k: vars_[k] for k in order}

    if fill_remaining:
        for k, v in vars_.items():
            if k not in reordered:
                reordered[k] = v

    set_profile(profile, reordered)
    return reordered


def move_key(profile: str, key: str, position: int) -> dict:
    """Move *key* to *position* (0-based) in the profile's variable dict.

    All other keys retain their relative order.  Persists the result and
    returns the updated variable dict.

    Raises ReorderError if the profile or key does not exist.
    """
    vars_ = get_profile(profile)
    if vars_ is None:
        raise ReorderError(f"Profile '{profile}' does not exist.")
    if key not in vars_:
        raise ReorderError(f"Key '{key}' not found in profile '{profile}'.")

    keys = [k for k in vars_ if k != key]
    position = max(0, min(position, len(keys)))
    keys.insert(position, key)

    reordered = {k: vars_[k] for k in keys}
    set_profile(profile, reordered)
    return reordered
