"""Tag management for environment profiles."""

from __future__ import annotations

from typing import Dict, List

from envctl.storage import load_profiles, save_profiles


class TagError(Exception):
    """Raised when a tag operation fails."""


TAGS_KEY = "__tags__"


def _get_tags(profile: dict) -> List[str]:
    """Return the tag list for a profile dict, defaulting to empty."""
    return profile.get(TAGS_KEY, [])


def add_tag(profile_name: str, tag: str) -> List[str]:
    """Add *tag* to *profile_name*. Returns the updated tag list."""
    profiles = load_profiles()
    if profile_name not in profiles:
        raise TagError(f"Profile '{profile_name}' does not exist.")
    tag = tag.strip()
    if not tag:
        raise TagError("Tag must not be empty.")
    tags = _get_tags(profiles[profile_name])
    if tag in tags:
        raise TagError(f"Tag '{tag}' already exists on profile '{profile_name}'.")
    tags.append(tag)
    profiles[profile_name][TAGS_KEY] = tags
    save_profiles(profiles)
    return tags


def remove_tag(profile_name: str, tag: str) -> List[str]:
    """Remove *tag* from *profile_name*. Returns the updated tag list."""
    profiles = load_profiles()
    if profile_name not in profiles:
        raise TagError(f"Profile '{profile_name}' does not exist.")
    tags = _get_tags(profiles[profile_name])
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found on profile '{profile_name}'.")
    tags.remove(tag)
    profiles[profile_name][TAGS_KEY] = tags
    save_profiles(profiles)
    return tags


def list_tags(profile_name: str) -> List[str]:
    """Return all tags for *profile_name*."""
    profiles = load_profiles()
    if profile_name not in profiles:
        raise TagError(f"Profile '{profile_name}' does not exist.")
    return list(_get_tags(profiles[profile_name]))


def find_by_tag(tag: str) -> List[str]:
    """Return names of all profiles that carry *tag*."""
    profiles = load_profiles()
    return [
        name
        for name, data in profiles.items()
        if tag in _get_tags(data)
    ]
