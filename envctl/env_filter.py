"""Filter profile variables by key pattern, value pattern, or both."""

from __future__ import annotations

import fnmatch
from typing import Dict, List, Optional

from envctl.storage import get_profile, set_profile


class FilterError(Exception):
    """Raised when a filter operation fails."""


def filter_profile(
    profile: str,
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    invert: bool = False,
    case_sensitive: bool = False,
) -> Dict[str, str]:
    """Return a dict of variables from *profile* that match the given patterns.

    At least one of *key_pattern* or *value_pattern* must be provided.
    Both patterns use Unix shell-style wildcards (fnmatch).
    When *invert* is True the non-matching variables are returned instead.
    """
    if key_pattern is None and value_pattern is None:
        raise FilterError("At least one of key_pattern or value_pattern must be provided.")

    variables = get_profile(profile)
    if variables is None:
        raise FilterError(f"Profile '{profile}' does not exist.")

    def _match(key: str, value: str) -> bool:
        k = key if case_sensitive else key.lower()
        v = value if case_sensitive else value.lower()
        kp = key_pattern if (key_pattern is None or case_sensitive) else key_pattern.lower()
        vp = value_pattern if (value_pattern is None or case_sensitive) else value_pattern.lower()

        key_ok = fnmatch.fnmatch(k, kp) if kp is not None else True
        val_ok = fnmatch.fnmatch(v, vp) if vp is not None else True
        return key_ok and val_ok

    result = {
        k: v for k, v in variables.items()
        if _match(k, v) != invert
    }
    return result


def apply_filter(
    profile: str,
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    invert: bool = False,
    case_sensitive: bool = False,
) -> Dict[str, str]:
    """Filter *profile* in-place, removing non-matching variables, and persist.

    Returns the surviving variables.
    """
    kept = filter_profile(
        profile,
        key_pattern=key_pattern,
        value_pattern=value_pattern,
        invert=invert,
        case_sensitive=case_sensitive,
    )
    set_profile(profile, kept)
    return kept
