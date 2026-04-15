"""Clone profiles with optional variable overrides."""

from __future__ import annotations

from typing import Dict, Optional

from envctl.storage import get_profile, load_profiles, save_profiles


class CloneError(Exception):
    """Raised when a clone operation fails."""


def clone_profile(
    source: str,
    dest: str,
    overrides: Optional[Dict[str, str]] = None,
    *,
    store_path=None,
) -> Dict[str, str]:
    """Clone *source* profile into *dest*, applying optional variable overrides.

    Parameters
    ----------
    source:
        Name of the existing profile to clone.
    dest:
        Name for the new profile.  Must not already exist.
    overrides:
        Key/value pairs that will be set (or added) on the cloned profile.
    store_path:
        Optional path override for the backing store (used in tests).

    Returns
    -------
    dict
        The variables of the newly created profile.
    """
    kwargs = {"store_path": store_path} if store_path is not None else {}

    src_vars = get_profile(source, **kwargs)
    if src_vars is None:
        raise CloneError(f"Source profile '{source}' does not exist.")

    profiles = load_profiles(**kwargs)
    if dest in profiles:
        raise CloneError(f"Destination profile '{dest}' already exists.")

    new_vars: Dict[str, str] = dict(src_vars)
    if overrides:
        new_vars.update(overrides)

    profiles[dest] = new_vars
    save_profiles(profiles, **kwargs)
    return new_vars


def clone_with_prefix(
    source: str,
    dest: str,
    prefix: str,
    *,
    store_path=None,
) -> Dict[str, str]:
    """Clone *source* into *dest*, prefixing every variable name with *prefix*."""
    kwargs = {"store_path": store_path} if store_path is not None else {}

    src_vars = get_profile(source, **kwargs)
    if src_vars is None:
        raise CloneError(f"Source profile '{source}' does not exist.")

    profiles = load_profiles(**kwargs)
    if dest in profiles:
        raise CloneError(f"Destination profile '{dest}' already exists.")

    new_vars = {f"{prefix}{k}": v for k, v in src_vars.items()}
    profiles[dest] = new_vars
    save_profiles(profiles, **kwargs)
    return new_vars
