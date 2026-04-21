"""Namespace support: partition profile variables by prefix namespace."""

from __future__ import annotations

from typing import Dict, List, Optional

from envctl.storage import get_profile, set_profile


class NamespaceError(Exception):
    """Raised when a namespace operation fails."""


def _sep(namespace: str) -> str:
    return f"{namespace.rstrip('_')}_"


def list_namespaces(profile_name: str) -> List[str]:
    """Return sorted unique namespace prefixes found in the profile."""
    profile = get_profile(profile_name)
    if profile is None:
        raise NamespaceError(f"Profile '{profile_name}' not found.")
    seen: set[str] = set()
    for key in profile:
        if "_" in key:
            ns = key.split("_")[0]
            seen.add(ns)
    return sorted(seen)


def get_namespace(profile_name: str, namespace: str) -> Dict[str, str]:
    """Return only the variables that belong to *namespace* (prefix match)."""
    profile = get_profile(profile_name)
    if profile is None:
        raise NamespaceError(f"Profile '{profile_name}' not found.")
    prefix = _sep(namespace)
    return {k: v for k, v in profile.items() if k.startswith(prefix)}


def set_namespace(
    profile_name: str,
    namespace: str,
    variables: Dict[str, str],
    overwrite: bool = True,
) -> Dict[str, str]:
    """Bulk-write *variables* under *namespace* into the profile.

    Keys in *variables* that already include the namespace prefix are stored
    as-is; bare keys are prefixed automatically.
    """
    profile = get_profile(profile_name)
    if profile is None:
        raise NamespaceError(f"Profile '{profile_name}' not found.")
    if not namespace:
        raise NamespaceError("Namespace must be a non-empty string.")
    prefix = _sep(namespace)
    updated: Dict[str, str] = {}
    for raw_key, value in variables.items():
        full_key = raw_key if raw_key.startswith(prefix) else f"{prefix}{raw_key}"
        if not overwrite and full_key in profile:
            continue
        profile[full_key] = value
        updated[full_key] = value
    set_profile(profile_name, profile)
    return updated


def delete_namespace(profile_name: str, namespace: str) -> List[str]:
    """Remove all variables belonging to *namespace* from the profile."""
    profile = get_profile(profile_name)
    if profile is None:
        raise NamespaceError(f"Profile '{profile_name}' not found.")
    prefix = _sep(namespace)
    to_delete = [k for k in profile if k.startswith(prefix)]
    for key in to_delete:
        del profile[key]
    set_profile(profile_name, profile)
    return to_delete
