"""Promote a profile's variables into another profile (e.g. staging -> production)."""

from typing import Optional
from envctl.storage import load_profiles, save_profiles


class PromoteError(Exception):
    pass


def promote_profile(
    source: str,
    target: str,
    keys: Optional[list[str]] = None,
    overwrite: bool = False,
) -> dict[str, str]:
    """Copy variables from *source* into *target*.

    Args:
        source:    Name of the profile to promote from.
        target:    Name of the profile to promote into.
        keys:      Optional list of specific variable names to promote.
                   When *None* all variables from source are promoted.
        overwrite: When *True*, existing keys in *target* are replaced.

    Returns:
        A dict of the variables that were actually written to *target*.

    Raises:
        PromoteError: If either profile does not exist, or source == target.
    """
    if source == target:
        raise PromoteError("Source and target profiles must be different.")

    profiles = load_profiles()

    if source not in profiles:
        raise PromoteError(f"Source profile '{source}' does not exist.")
    if target not in profiles:
        raise PromoteError(f"Target profile '{target}' does not exist.")

    src_vars: dict[str, str] = profiles[source].get("variables", {})
    tgt_vars: dict[str, str] = profiles[target].get("variables", {})

    candidates = {k: v for k, v in src_vars.items() if keys is None or k in keys}

    if keys:
        missing = set(keys) - set(src_vars)
        if missing:
            raise PromoteError(
                f"Keys not found in source profile '{source}': {', '.join(sorted(missing))}"
            )

    promoted: dict[str, str] = {}
    for k, v in candidates.items():
        if overwrite or k not in tgt_vars:
            tgt_vars[k] = v
            promoted[k] = v

    profiles[target]["variables"] = tgt_vars
    save_profiles(profiles)
    return promoted
