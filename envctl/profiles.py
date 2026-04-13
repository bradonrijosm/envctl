"""Business logic for profile management operations."""

from typing import Dict, List, Optional, Tuple

from envctl import storage


class ProfileError(Exception):
    """Raised when a profile operation fails."""


def create_profile(name: str, variables: Dict[str, str]) -> None:
    """Create a new profile. Raises ProfileError if it already exists."""
    if storage.get_profile(name) is not None:
        raise ProfileError(f"Profile '{name}' already exists. Use update to modify it.")
    storage.set_profile(name, variables)


def update_profile(name: str, variables: Dict[str, str], merge: bool = False) -> None:
    """Update an existing profile. Raises ProfileError if not found."""
    existing = storage.get_profile(name)
    if existing is None:
        raise ProfileError(f"Profile '{name}' does not exist. Use create to add it.")
    if merge:
        existing.update(variables)
        storage.set_profile(name, existing)
    else:
        storage.set_profile(name, variables)


def remove_profile(name: str) -> None:
    """Remove a profile by name. Raises ProfileError if not found."""
    if not storage.delete_profile(name):
        raise ProfileError(f"Profile '{name}' does not exist.")


def get_profile(name: str) -> Dict[str, str]:
    """Retrieve a profile's variables. Raises ProfileError if not found."""
    profile = storage.get_profile(name)
    if profile is None:
        raise ProfileError(f"Profile '{name}' does not exist.")
    return profile


def list_profiles() -> List[str]:
    """Return all stored profile names."""
    return storage.list_profile_names()


def export_shell(name: str) -> str:
    """Generate shell export statements for a profile."""
    variables = get_profile(name)
    lines = [f"export {k}={v!r}" for k, v in sorted(variables.items())]
    return "\n".join(lines)
