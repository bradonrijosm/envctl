"""env_chain.py – Chain multiple profiles together, resolving variables in order.

Later profiles in the chain override earlier ones (like shell PATH layering).
"""
from __future__ import annotations

from typing import Dict, List, Optional

from envctl.storage import get_profile, load_profiles


class ChainError(Exception):
    """Raised when a profile chain operation fails."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_chain_path():
    from envctl.storage import get_store_path
    import pathlib
    return pathlib.Path(get_store_path()).parent / "chains.json"


def _load_chains() -> Dict[str, List[str]]:
    import json
    path = _get_chain_path()
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_chains(chains: Dict[str, List[str]]) -> None:
    import json
    path = _get_chain_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(chains, fh, indent=2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_chain(name: str, profile_names: List[str]) -> None:
    """Define a named chain of profiles."""
    if not profile_names:
        raise ChainError("A chain must contain at least one profile.")
    all_profiles = load_profiles()
    for pname in profile_names:
        if pname not in all_profiles:
            raise ChainError(f"Profile '{pname}' does not exist.")
    chains = _load_chains()
    if name in chains:
        raise ChainError(f"Chain '{name}' already exists.")
    chains[name] = list(profile_names)
    _save_chains(chains)


def delete_chain(name: str) -> None:
    """Remove a named chain."""
    chains = _load_chains()
    if name not in chains:
        raise ChainError(f"Chain '{name}' does not exist.")
    del chains[name]
    _save_chains(chains)


def get_chain(name: str) -> Optional[List[str]]:
    """Return the ordered list of profile names for a chain, or None."""
    return _load_chains().get(name)


def list_chains() -> Dict[str, List[str]]:
    """Return all defined chains."""
    return _load_chains()


def resolve_chain(name: str) -> Dict[str, str]:
    """Merge all profiles in a chain; later profiles win on key conflicts."""
    chains = _load_chains()
    if name not in chains:
        raise ChainError(f"Chain '{name}' does not exist.")
    merged: Dict[str, str] = {}
    for pname in chains[name]:
        profile = get_profile(pname)
        if profile is None:
            raise ChainError(f"Profile '{pname}' in chain '{name}' no longer exists.")
        merged.update(profile)
    return merged
