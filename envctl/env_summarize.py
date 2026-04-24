"""Summarize one or more profiles into a human-readable report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envctl.storage import get_profile, load_profiles


class SummarizeError(Exception):
    """Raised when summarization fails."""


@dataclass
class ProfileSummary:
    name: str
    total_keys: int
    empty_keys: List[str] = field(default_factory=list)
    longest_key: Optional[str] = None
    shortest_key: Optional[str] = None
    avg_key_length: float = 0.0
    unique_values: int = 0


def summarize_profile(profile_name: str) -> ProfileSummary:
    """Return a summary for a single named profile."""
    variables = get_profile(profile_name)
    if variables is None:
        raise SummarizeError(f"Profile '{profile_name}' does not exist.")

    if not variables:
        return ProfileSummary(name=profile_name, total_keys=0)

    keys = list(variables.keys())
    empty_keys = [k for k, v in variables.items() if v == ""]
    key_lengths = [len(k) for k in keys]
    avg_len = sum(key_lengths) / len(key_lengths)
    longest = max(keys, key=len)
    shortest = min(keys, key=len)
    unique_vals = len(set(v for v in variables.values() if v != ""))

    return ProfileSummary(
        name=profile_name,
        total_keys=len(keys),
        empty_keys=empty_keys,
        longest_key=longest,
        shortest_key=shortest,
        avg_key_length=round(avg_len, 2),
        unique_values=unique_vals,
    )


def summarize_all_profiles() -> Dict[str, ProfileSummary]:
    """Return summaries for every profile in the store."""
    profiles = load_profiles()
    if not profiles:
        return {}
    return {name: summarize_profile(name) for name in profiles}


def format_summary(summary: ProfileSummary) -> str:
    """Render a ProfileSummary as a multi-line string."""
    lines = [
        f"Profile : {summary.name}",
        f"  Total keys    : {summary.total_keys}",
        f"  Empty keys    : {len(summary.empty_keys)}",
        f"  Longest key   : {summary.longest_key or '-'}",
        f"  Shortest key  : {summary.shortest_key or '-'}",
        f"  Avg key length: {summary.avg_key_length}",
        f"  Unique values : {summary.unique_values}",
    ]
    if summary.empty_keys:
        lines.append("  Empty key list: " + ", ".join(summary.empty_keys))
    return "\n".join(lines)
