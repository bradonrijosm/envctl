"""Scope management: associate profiles with named scopes (e.g. project dirs)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envctl.storage import get_store_path, get_profile


class ScopeError(Exception):
    """Raised on scope operation failures."""


def _get_scope_path() -> Path:
    return get_store_path().parent / "scopes.json"


def _load_scopes() -> Dict[str, str]:
    """Return mapping of scope_name -> profile_name."""
    p = _get_scope_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_scopes(scopes: Dict[str, str]) -> None:
    _get_scope_path().write_text(json.dumps(scopes, indent=2))


def bind_scope(scope: str, profile: str) -> None:
    """Bind *scope* to *profile*, overwriting any existing binding."""
    if get_profile(profile) is None:
        raise ScopeError(f"Profile '{profile}' does not exist.")
    scopes = _load_scopes()
    scopes[scope] = profile
    _save_scopes(scopes)


def unbind_scope(scope: str) -> None:
    """Remove the binding for *scope*."""
    scopes = _load_scopes()
    if scope not in scopes:
        raise ScopeError(f"Scope '{scope}' is not bound.")
    del scopes[scope]
    _save_scopes(scopes)


def resolve_scope(scope: str) -> Optional[str]:
    """Return the profile name bound to *scope*, or None if unbound."""
    return _load_scopes().get(scope)


def list_scopes() -> List[Dict[str, str]]:
    """Return all scopes sorted by name as list of {scope, profile} dicts."""
    scopes = _load_scopes()
    return [{"scope": k, "profile": v} for k, v in sorted(scopes.items())]
