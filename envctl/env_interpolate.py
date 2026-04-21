"""env_interpolate.py – Interpolate shell-style variable references within a profile.

Supports ``$VAR`` and ``${VAR}`` syntax.  References are resolved only within
the *same* profile (for cross-profile references see ``template.py``).

Example
-------
    BASE=/opt/myapp
    BIN=$BASE/bin          ->  BIN=/opt/myapp/bin
    CONF=${BASE}/conf      ->  CONF=/opt/myapp/conf

Circular references raise ``InterpolateError``.
"""

from __future__ import annotations

import re
from typing import Dict, Optional

from envctl.storage import get_profile, set_profile

# ---------------------------------------------------------------------------
# Regex – matches $VAR or ${VAR}; group 1 = bare name, group 2 = braced name
# ---------------------------------------------------------------------------
_REF_RE = re.compile(r"\$(?:(\w+)|\{(\w+)\})")


class InterpolateError(Exception):
    """Raised when interpolation cannot be completed."""


def _resolve_value(
    key: str,
    variables: Dict[str, str],
    resolved: Dict[str, str],
    resolving: set,
) -> str:
    """Recursively resolve *key* within *variables*.

    Parameters
    ----------
    key:        The variable name to resolve.
    variables:  Raw variable dict for the profile.
    resolved:   Cache of already-resolved values (mutated in place).
    resolving:  Set of keys currently being resolved (cycle detection).
    """
    if key in resolved:
        return resolved[key]

    if key not in variables:
        raise InterpolateError(f"Variable '{key}' referenced but not defined in profile.")

    if key in resolving:
        cycle = " -> ".join(sorted(resolving)) + f" -> {key}"
        raise InterpolateError(f"Circular reference detected: {cycle}")

    resolving.add(key)
    raw = variables[key]

    def _replace(match: re.Match) -> str:  # noqa: ANN001
        ref_name = match.group(1) or match.group(2)
        return _resolve_value(ref_name, variables, resolved, resolving)

    value = _REF_RE.sub(_replace, raw)
    resolving.discard(key)
    resolved[key] = value
    return value


def interpolate_profile(
    profile_name: str,
    *,
    save: bool = True,
    store_path: Optional[str] = None,
) -> Dict[str, str]:
    """Resolve all ``$VAR`` / ``${VAR}`` references inside *profile_name*.

    Parameters
    ----------
    profile_name:
        Name of the profile to interpolate.
    save:
        If ``True`` (default), persist the resolved variables back to the
        store so subsequent reads see the expanded values.
    store_path:
        Optional override for the store file path (used in tests).

    Returns
    -------
    Dict[str, str]
        The fully-resolved variable mapping.

    Raises
    ------
    InterpolateError
        If the profile does not exist, a referenced variable is missing, or a
        circular reference is detected.
    """
    kwargs = {"store_path": store_path} if store_path else {}
    variables: Optional[Dict[str, str]] = get_profile(profile_name, **kwargs)

    if variables is None:
        raise InterpolateError(f"Profile '{profile_name}' does not exist.")

    resolved: Dict[str, str] = {}
    resolving: set = set()

    for key in variables:
        _resolve_value(key, variables, resolved, resolving)

    if save:
        set_profile(profile_name, resolved, **kwargs)

    return resolved
