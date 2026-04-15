"""env_set.py — Bulk set/unset variables in a profile with optional dry-run support."""

from __future__ import annotations

from typing import Dict, List, Optional

from envctl.storage import get_profile, set_profile
from envctl.validate import is_valid_var_name, is_valid_profile_name


class EnvSetError(Exception):
    """Raised when a bulk set/unset operation fails."""


def bulk_set(
    profile_name: str,
    variables: Dict[str, str],
    *,
    overwrite: bool = True,
    dry_run: bool = False,
) -> Dict[str, str]:
    """Set one or more variables in *profile_name*.

    Parameters
    ----------
    profile_name:
        Target profile.
    variables:
        Mapping of variable names to values to set.
    overwrite:
        When *False*, existing keys are left unchanged.
    dry_run:
        When *True*, compute and return the resulting vars without persisting.

    Returns the resulting variable mapping after the operation.
    """
    if not is_valid_profile_name(profile_name):
        raise EnvSetError(f"Invalid profile name: {profile_name!r}")

    invalid = [k for k in variables if not is_valid_var_name(k)]
    if invalid:
        raise EnvSetError(f"Invalid variable name(s): {', '.join(invalid)}")

    current = get_profile(profile_name)
    if current is None:
        raise EnvSetError(f"Profile {profile_name!r} does not exist.")

    result = dict(current)
    for key, value in variables.items():
        if not overwrite and key in result:
            continue
        result[key] = value

    if not dry_run:
        set_profile(profile_name, result)

    return result


def bulk_unset(
    profile_name: str,
    keys: List[str],
    *,
    dry_run: bool = False,
) -> Dict[str, str]:
    """Remove one or more variables from *profile_name*.

    Missing keys are silently ignored.
    Returns the resulting variable mapping after the operation.
    """
    if not is_valid_profile_name(profile_name):
        raise EnvSetError(f"Invalid profile name: {profile_name!r}")

    current = get_profile(profile_name)
    if current is None:
        raise EnvSetError(f"Profile {profile_name!r} does not exist.")

    result = {k: v for k, v in current.items() if k not in keys}

    if not dry_run:
        set_profile(profile_name, result)

    return result
