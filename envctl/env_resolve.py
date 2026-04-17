"""Resolve final variable values for a profile, applying templates, inheritance, and aliases."""

from typing import Dict, Optional
from envctl.storage import get_profile
from envctl.template import render_profile, TemplateError
from envctl.alias import resolve_alias, AliasError


class ResolveError(Exception):
    pass


def resolve_profile_name(name: str, store_path=None) -> str:
    """Resolve an alias to a real profile name, or return as-is."""
    kwargs = {"store_path": store_path} if store_path else {}
    try:
        return resolve_alias(name, **kwargs)
    except AliasError:
        return name


def resolve_profile_vars(
    name: str,
    all_profiles: Optional[Dict[str, Dict[str, str]]] = None,
    store_path=None,
) -> Dict[str, str]:
    """Return fully resolved variables for a profile.

    1. Resolves alias -> real profile name.
    2. Loads raw variables.
    3. Renders template references (${profile.VAR} syntax).
    """
    kwargs = {"store_path": store_path} if store_path else {}

    real_name = resolve_profile_name(name, store_path=store_path)

    raw = get_profile(real_name, **kwargs)
    if raw is None:
        raise ResolveError(f"Profile '{real_name}' not found.")

    if all_profiles is None:
        from envctl.storage import load_profiles
        all_profiles = load_profiles(**kwargs)

    try:
        resolved = render_profile(real_name, all_profiles)
    except TemplateError as exc:
        raise ResolveError(str(exc)) from exc

    return resolved


def resolve_to_env_dict(name: str, store_path=None) -> Dict[str, str]:
    """Convenience wrapper returning a plain dict suitable for os.environ injection."""
    return resolve_profile_vars(name, store_path=store_path)
