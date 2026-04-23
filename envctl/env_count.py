"""Count and summarize variable statistics across profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envctl.storage import get_profile, load_profiles


class CountError(Exception):
    """Raised when a count operation fails."""


@dataclass
class ProfileCount:
    name: str
    total: int
    empty: int
    non_empty: int
    unique_values: int


@dataclass
class CountSummary:
    profiles: List[ProfileCount] = field(default_factory=list)
    grand_total: int = 0
    grand_empty: int = 0
    grand_non_empty: int = 0


def count_profile(profile_name: str) -> ProfileCount:
    """Return variable counts for a single profile."""
    variables = get_profile(profile_name)
    if variables is None:
        raise CountError(f"Profile '{profile_name}' not found.")

    total = len(variables)
    empty = sum(1 for v in variables.values() if v == "")
    non_empty = total - empty
    unique_values = len(set(variables.values()))

    return ProfileCount(
        name=profile_name,
        total=total,
        empty=empty,
        non_empty=non_empty,
        unique_values=unique_values,
    )


def count_all_profiles(tag: Optional[str] = None) -> CountSummary:
    """Return variable counts across all profiles.

    If *tag* is provided only profiles tagged with that value are included.
    Tag filtering is best-effort: profiles whose names appear in the tag index
    are included; when no tag module is available all profiles are counted.
    """
    all_profiles = load_profiles()

    names = list(all_profiles.keys())

    if tag is not None:
        try:
            from envctl.tags import list_tags  # noqa: PLC0415

            names = [n for n in names if tag in list_tags(n)]
        except Exception:  # pragma: no cover
            pass

    summary = CountSummary()
    for name in names:
        pc = count_profile(name)
        summary.profiles.append(pc)
        summary.grand_total += pc.total
        summary.grand_empty += pc.empty
        summary.grand_non_empty += pc.non_empty

    return summary
