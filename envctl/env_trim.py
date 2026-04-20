"""env_trim.py — Strip leading/trailing whitespace from profile variable values."""

from __future__ import annotations

from typing import Dict, List

from envctl.storage import get_profile, set_profile


class TrimError(Exception):
    """Raised when a trim operation fails."""


def trim_profile(
    profile_name: str,
    *,
    keys: List[str] | None = None,
    dry_run: bool = False,
) -> Dict[str, str]:
    """Strip whitespace from values in *profile_name*.

    Args:
        profile_name: Name of the profile to trim.
        keys: Optional list of specific keys to trim.  When *None* all keys
              are processed.
        dry_run: When *True* the store is not updated; the would-be result is
                 returned for inspection.

    Returns:
        A mapping of ``{key: trimmed_value}`` for every key whose value
        actually changed.

    Raises:
        TrimError: If the profile does not exist.
    """
    variables = get_profile(profile_name)
    if variables is None:
        raise TrimError(f"Profile '{profile_name}' does not exist.")

    target_keys = keys if keys is not None else list(variables.keys())

    changed: Dict[str, str] = {}
    updated = dict(variables)

    for key in target_keys:
        if key not in variables:
            continue
        original = variables[key]
        trimmed = original.strip()
        if trimmed != original:
            changed[key] = trimmed
            updated[key] = trimmed

    if changed and not dry_run:
        set_profile(profile_name, updated)

    return changed


def trim_all_profiles(
    *,
    dry_run: bool = False,
) -> Dict[str, Dict[str, str]]:
    """Apply :func:`trim_profile` to every profile in the store.

    Returns:
        A mapping of ``{profile_name: {key: trimmed_value}}`` for profiles
        that had at least one change.
    """
    from envctl.storage import load_profiles

    profiles = load_profiles()
    results: Dict[str, Dict[str, str]] = {}

    for name in profiles:
        changed = trim_profile(name, dry_run=dry_run)
        if changed:
            results[name] = changed

    return results
