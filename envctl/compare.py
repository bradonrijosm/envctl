"""Profile comparison utilities — summarise how two profiles relate."""

from dataclasses import dataclass, field
from typing import Dict, List

from envctl.storage import get_profile


class CompareError(Exception):
    """Raised when a comparison cannot be completed."""


@dataclass
class CompareResult:
    profile_a: str
    profile_b: str
    only_in_a: Dict[str, str] = field(default_factory=dict)
    only_in_b: Dict[str, str] = field(default_factory=dict)
    in_both_same: Dict[str, str] = field(default_factory=dict)
    in_both_different: Dict[str, tuple] = field(default_factory=dict)  # key -> (val_a, val_b)

    @property
    def are_identical(self) -> bool:
        return not self.only_in_a and not self.only_in_b and not self.in_both_different

    @property
    def similarity_pct(self) -> float:
        total = len(self.only_in_a) + len(self.only_in_b) + len(self.in_both_same) + len(self.in_both_different)
        if total == 0:
            return 100.0
        return round(len(self.in_both_same) / total * 100, 1)


def compare_profiles(name_a: str, name_b: str) -> CompareResult:
    """Compare two named profiles and return a CompareResult."""
    vars_a = get_profile(name_a)
    if vars_a is None:
        raise CompareError(f"Profile '{name_a}' not found.")
    vars_b = get_profile(name_b)
    if vars_b is None:
        raise CompareError(f"Profile '{name_b}' not found.")

    result = CompareResult(profile_a=name_a, profile_b=name_b)
    keys = set(vars_a) | set(vars_b)

    for key in keys:
        in_a = key in vars_a
        in_b = key in vars_b
        if in_a and not in_b:
            result.only_in_a[key] = vars_a[key]
        elif in_b and not in_a:
            result.only_in_b[key] = vars_b[key]
        elif vars_a[key] == vars_b[key]:
            result.in_both_same[key] = vars_a[key]
        else:
            result.in_both_different[key] = (vars_a[key], vars_b[key])

    return result


def format_compare(result: CompareResult) -> List[str]:
    """Return a list of human-readable lines describing the comparison."""
    lines: List[str] = []
    a, b = result.profile_a, result.profile_b

    if result.are_identical:
        lines.append(f"Profiles '{a}' and '{b}' are identical ({len(result.in_both_same)} vars).")
        return lines

    lines.append(f"Comparing '{a}' vs '{b}'  (similarity: {result.similarity_pct}%)")

    for key, val in sorted(result.only_in_a.items()):
        lines.append(f"  only in {a}: {key}={val}")
    for key, val in sorted(result.only_in_b.items()):
        lines.append(f"  only in {b}: {key}={val}")
    for key, (va, vb) in sorted(result.in_both_different.items()):
        lines.append(f"  changed:     {key}  {a}={va!r}  {b}={vb!r}")
    for key in sorted(result.in_both_same):
        lines.append(f"  same:        {key}")

    return lines
