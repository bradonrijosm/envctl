"""Diff utilities for comparing environment profiles."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class DiffError(Exception):
    pass


def diff_profiles(
    base: Dict[str, str],
    target: Dict[str, str],
    show_unchanged: bool = False,
) -> List[DiffEntry]:
    """Compare two variable dicts and return a list of DiffEntry results."""
    entries: List[DiffEntry] = []
    all_keys = sorted(set(base) | set(target))

    for key in all_keys:
        in_base = key in base
        in_target = key in target

        if in_base and not in_target:
            entries.append(DiffEntry(key=key, status="removed", old_value=base[key]))
        elif in_target and not in_base:
            entries.append(DiffEntry(key=key, status="added", new_value=target[key]))
        elif base[key] != target[key]:
            entries.append(
                DiffEntry(
                    key=key,
                    status="changed",
                    old_value=base[key],
                    new_value=target[key],
                )
            )
        elif show_unchanged:
            entries.append(
                DiffEntry(key=key, status="unchanged", old_value=base[key], new_value=target[key])
            )

    return entries


def format_diff(entries: List[DiffEntry], color: bool = True) -> str:
    """Render diff entries as a human-readable string."""
    if not entries:
        return "(no differences)"

    lines = []
    symbols = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}
    colors = {"added": "\033[32m", "removed": "\033[31m", "changed": "\033[33m", "unchanged": ""}
    reset = "\033[0m"

    for entry in entries:
        sym = symbols[entry.status]
        prefix = (colors[entry.status] if color else "") + sym
        suffix = reset if color else ""

        if entry.status == "added":
            lines.append(f"{prefix} {entry.key}={entry.new_value}{suffix}")
        elif entry.status == "removed":
            lines.append(f"{prefix} {entry.key}={entry.old_value}{suffix}")
        elif entry.status == "changed":
            lines.append(f"{prefix} {entry.key}: {entry.old_value!r} -> {entry.new_value!r}{suffix}")
        else:
            lines.append(f"{prefix} {entry.key}={entry.old_value}{suffix}")

    return "\n".join(lines)
