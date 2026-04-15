"""Search profiles by variable name or value patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional

from envctl.storage import load_profiles


class SearchError(Exception):
    """Raised when a search operation fails."""


@dataclass
class SearchMatch:
    profile: str
    key: str
    value: str


def search_by_key(
    pattern: str,
    *,
    case_sensitive: bool = False,
) -> List[SearchMatch]:
    """Return all variables whose key matches *pattern* (glob-style)."""
    profiles = load_profiles()
    results: List[SearchMatch] = []
    for profile_name, variables in profiles.items():
        for key, value in variables.items():
            candidate = key if case_sensitive else key.lower()
            pat = pattern if case_sensitive else pattern.lower()
            if fnmatch(candidate, pat):
                results.append(SearchMatch(profile=profile_name, key=key, value=value))
    return results


def search_by_value(
    pattern: str,
    *,
    case_sensitive: bool = False,
) -> List[SearchMatch]:
    """Return all variables whose value matches *pattern* (glob-style)."""
    profiles = load_profiles()
    results: List[SearchMatch] = []
    for profile_name, variables in profiles.items():
        for key, value in variables.items():
            candidate = value if case_sensitive else value.lower()
            pat = pattern if case_sensitive else pattern.lower()
            if fnmatch(candidate, pat):
                results.append(SearchMatch(profile=profile_name, key=key, value=value))
    return results


def search_profiles(
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    *,
    case_sensitive: bool = False,
) -> List[SearchMatch]:
    """Search by key pattern, value pattern, or both (AND logic)."""
    if key_pattern is None and value_pattern is None:
        raise SearchError("At least one of key_pattern or value_pattern must be provided.")

    key_matches = (
        {(m.profile, m.key) for m in search_by_key(key_pattern, case_sensitive=case_sensitive)}
        if key_pattern
        else None
    )
    value_matches = (
        {(m.profile, m.key) for m in search_by_value(value_pattern, case_sensitive=case_sensitive)}
        if value_pattern
        else None
    )

    if key_matches is not None and value_matches is not None:
        combined = key_matches & value_matches
    else:
        combined = key_matches or value_matches  # type: ignore[assignment]

    profiles = load_profiles()
    return [
        SearchMatch(profile=p, key=k, value=profiles[p][k])
        for p, k in sorted(combined)  # type: ignore[union-attr]
        if p in profiles and k in profiles[p]
    ]
