"""Masking sensitive environment variable values for safe display."""

from __future__ import annotations

from typing import Dict, List

from envctl.storage import get_profile


class MaskError(Exception):
    pass


_DEFAULT_SENSITIVE_PATTERNS = [
    "secret", "password", "passwd", "token", "key", "api_key",
    "auth", "credential", "private", "pwd",
]


def _is_sensitive(var_name: str, patterns: List[str]) -> bool:
    lower = var_name.lower()
    return any(p in lower for p in patterns)


def mask_value(value: str, reveal_chars: int = 4) -> str:
    """Return a masked version of *value*, revealing the last *reveal_chars* characters."""
    if len(value) <= reveal_chars:
        return "*" * len(value)
    return "*" * (len(value) - reveal_chars) + value[-reveal_chars:]


def mask_profile(
    profile_name: str,
    *,
    patterns: List[str] | None = None,
    reveal_chars: int = 4,
) -> Dict[str, str]:
    """Return a copy of the profile's variables with sensitive values masked.

    Args:
        profile_name: Name of the profile to mask.
        patterns: List of substrings that mark a key as sensitive.
                  Defaults to ``_DEFAULT_SENSITIVE_PATTERNS``.
        reveal_chars: How many trailing characters to reveal in masked values.

    Returns:
        Dict mapping variable names to (possibly masked) values.

    Raises:
        MaskError: If the profile does not exist.
    """
    if patterns is None:
        patterns = _DEFAULT_SENSITIVE_PATTERNS

    profile = get_profile(profile_name)
    if profile is None:
        raise MaskError(f"Profile '{profile_name}' not found.")

    result: Dict[str, str] = {}
    for key, value in profile.items():
        if _is_sensitive(key, patterns):
            result[key] = mask_value(value, reveal_chars=reveal_chars)
        else:
            result[key] = value
    return result
