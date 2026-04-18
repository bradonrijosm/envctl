"""Sort profile variables by key or value."""
from __future__ import annotations
from typing import Literal
from envctl.storage import get_profile, set_profile

SortBy = Literal["key", "value"]


class SortError(Exception):
    pass


def sort_profile(
    profile: str,
    by: SortBy = "key",
    reverse: bool = False,
) -> dict[str, str]:
    """Return variables of *profile* sorted by key or value.

    Persists the sorted order back to the store.
    """
    data = get_profile(profile)
    if data is None:
        raise SortError(f"Profile '{profile}' not found.")

    variables: dict[str, str] = data.get("variables", {})

    if by == "key":
        sorted_vars = dict(sorted(variables.items(), key=lambda kv: kv[0], reverse=reverse))
    elif by == "value":
        sorted_vars = dict(sorted(variables.items(), key=lambda kv: kv[1], reverse=reverse))
    else:
        raise SortError(f"Unknown sort field '{by}'. Use 'key' or 'value'.")

    updated = {**data, "variables": sorted_vars}
    set_profile(profile, updated)
    return sorted_vars
