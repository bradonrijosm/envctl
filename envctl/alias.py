"""Profile alias management for envctl."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envctl.storage import get_store_path, get_profile


class AliasError(Exception):
    """Raised when an alias operation fails."""


def _get_alias_path() -> Path:
    return get_store_path().parent / "aliases.json"


def _load_aliases() -> Dict[str, str]:
    path = _get_alias_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_aliases(aliases: Dict[str, str]) -> None:
    _get_alias_path().write_text(json.dumps(aliases, indent=2))


def add_alias(alias: str, profile_name: str) -> None:
    """Create an alias pointing to an existing profile."""
    if get_profile(profile_name) is None:
        raise AliasError(f"Profile '{profile_name}' does not exist.")
    aliases = _load_aliases()
    if alias in aliases:
        raise AliasError(f"Alias '{alias}' already exists (points to '{aliases[alias]}').")
    aliases[alias] = profile_name
    _save_aliases(aliases)


def remove_alias(alias: str) -> None:
    """Remove an existing alias."""
    aliases = _load_aliases()
    if alias not in aliases:
        raise AliasError(f"Alias '{alias}' does not exist.")
    del aliases[alias]
    _save_aliases(aliases)


def resolve_alias(alias: str) -> Optional[str]:
    """Return the profile name for an alias, or None if not found."""
    return _load_aliases().get(alias)


def list_aliases() -> Dict[str, str]:
    """Return all alias -> profile mappings."""
    return dict(_load_aliases())


def rename_alias(alias: str, new_alias: str) -> None:
    """Rename an alias key without changing the target profile."""
    aliases = _load_aliases()
    if alias not in aliases:
        raise AliasError(f"Alias '{alias}' does not exist.")
    if new_alias in aliases:
        raise AliasError(f"Alias '{new_alias}' already exists.")
    aliases[new_alias] = aliases.pop(alias)
    _save_aliases(aliases)
