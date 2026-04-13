"""Profile copy/clone functionality for envctl."""

from envctl.storage import load_profiles, save_profiles


class CopyError(Exception):
    """Raised when a copy operation fails."""


def copy_profile(source_name: str, dest_name: str, overwrite: bool = False) -> dict:
    """Copy an existing profile to a new name.

    Args:
        source_name: Name of the profile to copy from.
        dest_name: Name of the new profile.
        overwrite: If True, overwrite dest if it already exists.

    Returns:
        The newly created profile dict.

    Raises:
        CopyError: If source does not exist, dest already exists (and overwrite
                   is False), or source and dest are the same name.
    """
    if source_name == dest_name:
        raise CopyError(f"Source and destination profile names are the same: '{source_name}'")

    profiles = load_profiles()

    if source_name not in profiles:
        raise CopyError(f"Source profile '{source_name}' does not exist.")

    if dest_name in profiles and not overwrite:
        raise CopyError(
            f"Destination profile '{dest_name}' already exists. "
            "Use --overwrite to replace it."
        )

    new_profile = {
        "name": dest_name,
        "variables": dict(profiles[source_name].get("variables", {})),
    }

    profiles[dest_name] = new_profile
    save_profiles(profiles)
    return new_profile


def rename_profile(old_name: str, new_name: str, overwrite: bool = False) -> dict:
    """Rename a profile by copying it then removing the original.

    Args:
        old_name: Current profile name.
        new_name: Desired new profile name.
        overwrite: If True, overwrite new_name if it already exists.

    Returns:
        The renamed profile dict.

    Raises:
        CopyError: If old_name does not exist or new_name conflicts.
    """
    new_profile = copy_profile(old_name, new_name, overwrite=overwrite)

    profiles = load_profiles()
    profiles.pop(old_name, None)
    save_profiles(profiles)

    return new_profile
