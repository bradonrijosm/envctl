"""Rename a key within a profile, optionally across all profiles."""

from envctl.storage import get_profile, set_profile, load_profiles, save_profiles


class RenameKeyError(Exception):
    pass


def rename_key(profile_name: str, old_key: str, new_key: str, *, overwrite: bool = False) -> dict:
    """Rename *old_key* to *new_key* inside *profile_name*.

    Returns the updated variables dict.

    Raises:
        RenameKeyError: if the profile doesn't exist, old_key is missing,
                        or new_key already exists and overwrite=False.
    """
    variables = get_profile(profile_name)
    if variables is None:
        raise RenameKeyError(f"Profile '{profile_name}' not found.")

    if old_key not in variables:
        raise RenameKeyError(
            f"Key '{old_key}' does not exist in profile '{profile_name}'."
        )

    if new_key in variables and not overwrite:
        raise RenameKeyError(
            f"Key '{new_key}' already exists in profile '{profile_name}'. "
            "Use overwrite=True to replace it."
        )

    value = variables.pop(old_key)
    variables[new_key] = value
    set_profile(profile_name, variables)
    return variables


def rename_key_all_profiles(old_key: str, new_key: str, *, overwrite: bool = False) -> dict:
    """Rename *old_key* to *new_key* in every profile that contains it.

    Returns a mapping of {profile_name: updated_variables} for each profile
    that was modified.

    Raises:
        RenameKeyError: if new_key already exists in any profile and overwrite=False.
    """
    all_profiles = load_profiles()

    if not overwrite:
        conflicts = [
            name
            for name, variables in all_profiles.items()
            if old_key in variables and new_key in variables
        ]
        if conflicts:
            raise RenameKeyError(
                f"Key '{new_key}' already exists alongside '{old_key}' in profiles: "
                + ", ".join(conflicts)
                + ". Use overwrite=True to replace."
            )

    updated = {}
    for name, variables in all_profiles.items():
        if old_key in variables:
            value = variables.pop(old_key)
            variables[new_key] = value
            all_profiles[name] = variables
            updated[name] = variables

    if updated:
        save_profiles(all_profiles)

    return updated
