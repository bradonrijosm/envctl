"""Detect and remove duplicate values across a profile's variables."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envctl.storage import get_profile, set_profile


class DedupeError(Exception):
    """Raised when a deduplication operation fails."""


@dataclass
class DedupeResult:
    """Result of a deduplication scan or operation."""

    profile: str
    # Maps each duplicated value -> list of keys that share it
    duplicates: Dict[str, List[str]] = field(default_factory=dict)
    # Keys that were removed (kept the first occurrence)
    removed_keys: List[str] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)


def find_duplicates(profile_name: str) -> DedupeResult:
    """Scan *profile_name* and return a :class:`DedupeResult` describing
    every value that appears more than once.

    Raises :class:`DedupeError` if the profile does not exist.
    """
    variables = get_profile(profile_name)
    if variables is None:
        raise DedupeError(f"Profile '{profile_name}' does not exist.")

    seen: Dict[str, List[str]] = {}
    for key, value in variables.items():
        seen.setdefault(value, []).append(key)

    duplicates = {v: keys for v, keys in seen.items() if len(keys) > 1}
    return DedupeResult(profile=profile_name, duplicates=duplicates)


def dedupe_profile(
    profile_name: str,
    *,
    keep: str = "first",
    dry_run: bool = False,
) -> DedupeResult:
    """Remove duplicate-value keys from *profile_name*.

    Parameters
    ----------
    profile_name:
        Target profile.
    keep:
        ``"first"`` keeps the lexicographically first key; ``"last"`` keeps
        the lexicographically last key.
    dry_run:
        When *True* the profile is **not** modified; the result still
        describes what *would* be removed.

    Raises :class:`DedupeError` for missing profiles or an invalid *keep*
    value.
    """
    if keep not in ("first", "last"):
        raise DedupeError(f"Invalid keep strategy '{keep}': choose 'first' or 'last'.")

    result = find_duplicates(profile_name)
    if not result.has_duplicates:
        return result

    variables = get_profile(profile_name)  # type: ignore[assignment]
    to_remove: List[str] = []
    for _value, keys in result.duplicates.items():
        ordered = sorted(keys)
        survivors = ordered[:1] if keep == "first" else ordered[-1:]
        to_remove.extend(k for k in ordered if k not in survivors)

    result.removed_keys = sorted(to_remove)

    if not dry_run:
        updated = {k: v for k, v in variables.items() if k not in to_remove}
        set_profile(profile_name, updated)

    return result
