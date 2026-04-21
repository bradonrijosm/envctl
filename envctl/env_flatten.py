"""Flatten nested profile variable references into a single resolved dict."""

from __future__ import annotations

from typing import Dict, Optional

from envctl.storage import get_profile, load_profiles


class FlattenError(Exception):
    pass


MAX_DEPTH = 10


def _resolve_value(value: str, vars_: Dict[str, str], depth: int) -> str:
    """Expand ${VAR} references within a value using the given variable map."""
    if depth > MAX_DEPTH:
        raise FlattenError("Circular or too-deep variable reference detected.")
    import re

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key not in vars_:
            raise FlattenError(f"Variable '${{{key}}}' not found during flattening.")
        return _resolve_value(vars_[key], vars_, depth + 1)

    return re.sub(r"\$\{([^}]+)\}", replacer, value)


def flatten_profile(
    profile_name: str,
    *,
    base_profile: Optional[str] = None,
) -> Dict[str, str]:
    """Return a fully-resolved variable dict for *profile_name*.

    If *base_profile* is given its variables are merged in first (lower
    priority) before the target profile's own variables are applied.

    Args:
        profile_name: Name of the profile to flatten.
        base_profile: Optional name of a profile whose variables act as
            defaults before the target profile is applied.

    Returns:
        A dict of variable names to fully-resolved string values.

    Raises:
        FlattenError: If a profile is missing or a reference cannot be
            resolved.
    """
    profiles = load_profiles()

    if profile_name not in profiles:
        raise FlattenError(f"Profile '{profile_name}' does not exist.")

    merged: Dict[str, str] = {}

    if base_profile is not None:
        if base_profile not in profiles:
            raise FlattenError(f"Base profile '{base_profile}' does not exist.")
        merged.update(profiles[base_profile])

    merged.update(profiles[profile_name])

    resolved: Dict[str, str] = {}
    for key, value in merged.items():
        resolved[key] = _resolve_value(value, merged, depth=0)

    return resolved
