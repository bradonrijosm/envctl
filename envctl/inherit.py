"""Profile inheritance: derive a profile from a base, overriding specific keys."""

from __future__ import annotations

from typing import Dict

from envctl.storage import get_profile, set_profile, load_profiles


class InheritError(Exception):
    """Raised when profile inheritance fails."""


def inherit_profile(
    base_name: str,
    derived_name: str,
    overrides: Dict[str, str],
    *,
    store_path=None,
) -> Dict[str, str]:
    """Create *derived_name* by merging *base_name* variables with *overrides*.

    The derived profile contains every variable from the base profile, with
    any keys present in *overrides* replaced by the override value.  The base
    profile is never modified.

    Raises InheritError if *base_name* does not exist or *derived_name*
    already exists.
    """
    kwargs = {} if store_path is None else {"store_path": store_path}

    base_vars = get_profile(base_name, **kwargs)
    if base_vars is None:
        raise InheritError(f"Base profile '{base_name}' does not exist.")

    profiles = load_profiles(**kwargs)
    if derived_name in profiles:
        raise InheritError(f"Derived profile '{derived_name}' already exists.")

    merged: Dict[str, str] = {**base_vars, **overrides}
    set_profile(derived_name, merged, **kwargs)
    return merged


def rebase_profile(
    profile_name: str,
    new_base_name: str,
    *,
    store_path=None,
) -> Dict[str, str]:
    """Re-apply *profile_name*'s own overrides on top of a new base.

    The current variables of *profile_name* are treated as overrides; they
    replace matching keys from *new_base_name*.  The result is saved back to
    *profile_name*.

    Raises InheritError if either profile does not exist.
    """
    kwargs = {} if store_path is None else {"store_path": store_path}

    new_base_vars = get_profile(new_base_name, **kwargs)
    if new_base_vars is None:
        raise InheritError(f"New base profile '{new_base_name}' does not exist.")

    current_vars = get_profile(profile_name, **kwargs)
    if current_vars is None:
        raise InheritError(f"Profile '{profile_name}' does not exist.")

    merged: Dict[str, str] = {**new_base_vars, **current_vars}
    set_profile(profile_name, merged, **kwargs)
    return merged
