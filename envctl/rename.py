"""Rename and clone profiles with optional variable filtering."""

from __future__ import annotations

from typing import Optional

from envctl.storage import load_profiles, save_profiles


class RenameError(Exception):
    """Raised when a rename or clone operation fails."""


def rename_profile(old_name: str, new_name: str) -> None:
    """Rename *old_name* to *new_name* in the store.

    Raises RenameError if *old_name* does not exist or *new_name* is already taken.
    """
    profiles = load_profiles()
    if old_name not in profiles:
        raise RenameError(f"Profile '{old_name}' does not exist.")
    if new_name in profiles:
        raise RenameError(f"Profile '{new_name}' already exists.")
    profiles[new_name] = profiles.pop(old_name)
    save_profiles(profiles)


def clone_profile(
    source: str,
    dest: str,
    *,
    include_keys: Optional[list[str]] = None,
    exclude_keys: Optional[list[str]] = None,
) -> dict[str, str]:
    """Clone *source* into a new profile *dest*.

    Optionally restrict which variables are copied:
    - *include_keys*: if provided, only these keys are copied.
    - *exclude_keys*: if provided, these keys are omitted.

    Returns the variables stored in the new profile.
    Raises RenameError if *source* does not exist or *dest* already exists.
    """
    profiles = load_profiles()
    if source not in profiles:
        raise RenameError(f"Profile '{source}' does not exist.")
    if dest in profiles:
        raise RenameError(f"Profile '{dest}' already exists.")

    variables: dict[str, str] = dict(profiles[source])

    if include_keys is not None:
        variables = {k: v for k, v in variables.items() if k in include_keys}
    if exclude_keys is not None:
        variables = {k: v for k, v in variables.items() if k not in exclude_keys}

    profiles[dest] = variables
    save_profiles(profiles)
    return variables
