"""Read-only mode for environment profiles.

Allows marking a profile as read-only so that no modifications
(set, unset, delete, rename, merge, etc.) can be applied to it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envctl.storage import get_store_path, get_profile


class ReadonlyError(Exception):
    """Raised when a read-only constraint is violated."""


def _get_readonly_path() -> Path:
    return get_store_path().parent / "readonly.json"


def _load_readonly() -> List[str]:
    path = _get_readonly_path()
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _save_readonly(names: List[str]) -> None:
    _get_readonly_path().write_text(json.dumps(sorted(set(names)), indent=2))


def mark_readonly(profile_name: str) -> None:
    """Mark *profile_name* as read-only.

    Raises ReadonlyError if the profile does not exist.
    Raises ReadonlyError if the profile is already marked read-only.
    """
    if get_profile(profile_name) is None:
        raise ReadonlyError(f"Profile '{profile_name}' does not exist.")
    names = _load_readonly()
    if profile_name in names:
        raise ReadonlyError(f"Profile '{profile_name}' is already read-only.")
    names.append(profile_name)
    _save_readonly(names)


def unmark_readonly(profile_name: str) -> None:
    """Remove the read-only flag from *profile_name*.

    Raises ReadonlyError if the profile is not currently marked read-only.
    """
    names = _load_readonly()
    if profile_name not in names:
        raise ReadonlyError(f"Profile '{profile_name}' is not marked read-only.")
    names.remove(profile_name)
    _save_readonly(names)


def is_readonly(profile_name: str) -> bool:
    """Return True if *profile_name* is currently marked read-only."""
    return profile_name in _load_readonly()


def assert_writable(profile_name: str) -> None:
    """Raise ReadonlyError if *profile_name* is read-only.

    Intended to be called at the start of any mutating operation.
    """
    if is_readonly(profile_name):
        raise ReadonlyError(
            f"Profile '{profile_name}' is read-only. "
            "Use 'envctl readonly remove' to unlock it."
        )


def list_readonly() -> List[str]:
    """Return a sorted list of all read-only profile names."""
    return sorted(_load_readonly())
