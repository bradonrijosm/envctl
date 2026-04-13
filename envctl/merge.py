"""Merge variables from one profile into another."""

from typing import Optional
from envctl.storage import load_profiles, save_profiles


class MergeError(Exception):
    pass


def merge_profiles(
    source: str,
    target: str,
    overwrite: bool = False,
) -> dict:
    """Merge variables from *source* profile into *target* profile.

    Parameters
    ----------
    source:
        Name of the profile whose variables are read.
    target:
        Name of the profile that receives the merged variables.
    overwrite:
        When *True*, keys present in both profiles are overwritten with
        the source value.  When *False* (default), existing keys in the
        target are left untouched.

    Returns
    -------
    dict
        The updated variable mapping for *target* after the merge.
    """
    profiles = load_profiles()

    if source not in profiles:
        raise MergeError(f"Source profile '{source}' does not exist.")
    if target not in profiles:
        raise MergeError(f"Target profile '{target}' does not exist.")
    if source == target:
        raise MergeError("Source and target profiles must be different.")

    src_vars: dict = profiles[source].get("variables", {})
    tgt_vars: dict = profiles[target].get("variables", {})

    if overwrite:
        merged = {**tgt_vars, **src_vars}
    else:
        merged = {**src_vars, **tgt_vars}

    profiles[target]["variables"] = merged
    save_profiles(profiles)
    return merged
