"""Case transformation utilities for profile variable keys and values."""

from typing import Dict, List
from envctl.storage import get_profile, set_profile


class CaseError(Exception):
    """Raised when a case transformation operation fails."""


CASE_MODES = ("upper", "lower", "title")


def _transform_key(key: str, mode: str) -> str:
    if mode == "upper":
        return key.upper()
    if mode == "lower":
        return key.lower()
    if mode == "title":
        return key.title()
    raise CaseError(f"Unknown mode: {mode!r}. Choose from {CASE_MODES}.")


def _transform_value(value: str, mode: str) -> str:
    if mode == "upper":
        return value.upper()
    if mode == "lower":
        return value.lower()
    if mode == "title":
        return value.title()
    raise CaseError(f"Unknown mode: {mode!r}. Choose from {CASE_MODES}.")


def transform_keys(profile_name: str, mode: str) -> Dict[str, str]:
    """Return a new variable dict with all keys transformed by *mode*.

    Raises CaseError if the profile does not exist or mode is invalid.
    Persists the transformed profile to the store.
    """
    if mode not in CASE_MODES:
        raise CaseError(f"Unknown mode: {mode!r}. Choose from {CASE_MODES}.")
    profile = get_profile(profile_name)
    if profile is None:
        raise CaseError(f"Profile {profile_name!r} not found.")
    transformed = {_transform_key(k, mode): v for k, v in profile.items()}
    set_profile(profile_name, transformed)
    return transformed


def transform_values(profile_name: str, mode: str) -> Dict[str, str]:
    """Return a new variable dict with all values transformed by *mode*.

    Raises CaseError if the profile does not exist or mode is invalid.
    Persists the transformed profile to the store.
    """
    if mode not in CASE_MODES:
        raise CaseError(f"Unknown mode: {mode!r}. Choose from {CASE_MODES}.")
    profile = get_profile(profile_name)
    if profile is None:
        raise CaseError(f"Profile {profile_name!r} not found.")
    transformed = {k: _transform_value(v, mode) for k, v in profile.items()}
    set_profile(profile_name, transformed)
    return transformed


def list_modes() -> List[str]:
    """Return the supported case transformation modes."""
    return list(CASE_MODES)
