"""Profile statistics and summary utilities."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envctl.storage import get_profile, load_profiles


class StatsError(Exception):
    pass


@dataclass
class ProfileStats:
    name: str
    var_count: int
    empty_count: int
    key_lengths: List[int] = field(default_factory=list)
    value_lengths: List[int] = field(default_factory=list)

    @property
    def avg_key_length(self) -> float:
        return sum(self.key_lengths) / len(self.key_lengths) if self.key_lengths else 0.0

    @property
    def avg_value_length(self) -> float:
        return sum(self.value_lengths) / len(self.value_lengths) if self.value_lengths else 0.0

    @property
    def longest_key(self) -> str | None:
        if not self.key_lengths:
            return None
        return str(max(self.key_lengths))


def profile_stats(name: str) -> ProfileStats:
    """Compute statistics for a single named profile."""
    profile = get_profile(name)
    if profile is None:
        raise StatsError(f"Profile '{name}' not found.")
    variables: Dict[str, str] = profile.get("variables", {})
    empty_count = sum(1 for v in variables.values() if v == "")
    key_lengths = [len(k) for k in variables]
    value_lengths = [len(v) for v in variables.values()]
    return ProfileStats(
        name=name,
        var_count=len(variables),
        empty_count=empty_count,
        key_lengths=key_lengths,
        value_lengths=value_lengths,
    )


def all_stats() -> List[ProfileStats]:
    """Return stats for every profile in the store."""
    profiles = load_profiles()
    return [profile_stats(name) for name in profiles]


def summary_report(stats_list: List[ProfileStats]) -> str:
    """Format a human-readable summary table."""
    if not stats_list:
        return "No profiles found."
    lines = [f"{'Profile':<30} {'Vars':>5} {'Empty':>6} {'AvgKeyLen':>10} {'AvgValLen':>10}"]
    lines.append("-" * 65)
    for s in stats_list:
        lines.append(
            f"{s.name:<30} {s.var_count:>5} {s.empty_count:>6} "
            f"{s.avg_key_length:>10.1f} {s.avg_value_length:>10.1f}"
        )
    return "\n".join(lines)
