"""Apply a diff as a patch to a target profile."""
from __future__ import annotations
from typing import Optional
from envctl.diff import diff_profiles, DiffEntry
from envctl.storage import get_profile, set_profile
from envctl.profiles import ProfileError


class PatchError(Exception):
    pass


def apply_diff(
    source: str,
    target: str,
    *,
    overwrite: bool = False,
    dry_run: bool = False,
) -> dict[str, str]:
    """Apply variables from *source* onto *target* using diff logic.

    - Keys only in source  -> added to target.
    - Keys changed between source and target -> updated only when overwrite=True.
    - Keys only in target  -> left untouched.

    Returns the resulting variable dict (not yet persisted when dry_run=True).
    """
    src_vars = get_profile(source)
    if src_vars is None:
        raise PatchError(f"Source profile '{source}' not found.")

    tgt_vars = get_profile(target)
    if tgt_vars is None:
        raise PatchError(f"Target profile '{target}' not found.")

    entries: list[DiffEntry] = diff_profiles(source, target, include_unchanged=True)

    result = dict(tgt_vars)

    for entry in entries:
        if entry.status == "added":          # in source only
            result[entry.key] = entry.value_a  # type: ignore[assignment]
        elif entry.status == "changed" and overwrite:
            result[entry.key] = entry.value_a  # type: ignore[assignment]
        # removed (only in target) and unchanged -> keep target value

    if not dry_run:
        set_profile(target, result)

    return result
