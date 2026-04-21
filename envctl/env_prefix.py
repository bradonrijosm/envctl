"""Prefix/strip key prefixes across environment variable profiles."""

from envctl.storage import get_profile, set_profile


class PrefixError(Exception):
    pass


def add_prefix(profile_name: str, prefix: str, *, overwrite: bool = False) -> dict:
    """Return a new vars dict with `prefix` prepended to every key.

    Args:
        profile_name: Name of the profile to transform.
        prefix: String to prepend to each key.
        overwrite: If False (default), raise PrefixError on key collision.

    Returns:
        The updated variables dict (already persisted).
    """
    if not prefix:
        raise PrefixError("prefix must be a non-empty string")

    profile = get_profile(profile_name)
    if profile is None:
        raise PrefixError(f"profile '{profile_name}' not found")

    old_vars: dict = profile.get("variables", {})
    new_vars: dict = {}

    for key, value in old_vars.items():
        new_key = f"{prefix}{key}"
        if new_key in old_vars and not overwrite:
            raise PrefixError(
                f"prefixed key '{new_key}' already exists in profile '{profile_name}'"
            )
        new_vars[new_key] = value

    profile["variables"] = new_vars
    set_profile(profile_name, profile)
    return new_vars


def strip_prefix(profile_name: str, prefix: str, *, ignore_missing: bool = False) -> dict:
    """Return a new vars dict with `prefix` removed from matching keys.

    Keys that do not start with `prefix` are left unchanged unless
    `ignore_missing` is False, in which case a PrefixError is raised.

    Args:
        profile_name: Name of the profile to transform.
        prefix: String to strip from the start of each key.
        ignore_missing: When True, silently skip keys that lack the prefix.

    Returns:
        The updated variables dict (already persisted).
    """
    if not prefix:
        raise PrefixError("prefix must be a non-empty string")

    profile = get_profile(profile_name)
    if profile is None:
        raise PrefixError(f"profile '{profile_name}' not found")

    old_vars: dict = profile.get("variables", {})
    new_vars: dict = {}

    for key, value in old_vars.items():
        if key.startswith(prefix):
            new_vars[key[len(prefix):]] = value
        elif ignore_missing:
            new_vars[key] = value
        else:
            raise PrefixError(
                f"key '{key}' does not start with prefix '{prefix}'"
            )

    profile["variables"] = new_vars
    set_profile(profile_name, profile)
    return new_vars
