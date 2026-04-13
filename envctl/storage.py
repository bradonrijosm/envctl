"""Storage module for managing environment profiles on disk."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

DEFAULT_STORE_DIR = Path.home() / ".envctl"
PROFILES_FILE = "profiles.json"


def get_store_path() -> Path:
    """Return the path to the envctl data directory."""
    store_dir = Path(os.environ.get("ENVCTL_HOME", DEFAULT_STORE_DIR))
    store_dir.mkdir(parents=True, exist_ok=True)
    return store_dir


def load_profiles() -> Dict[str, Dict[str, str]]:
    """Load all profiles from disk. Returns empty dict if none exist."""
    profiles_path = get_store_path() / PROFILES_FILE
    if not profiles_path.exists():
        return {}
    with profiles_path.open("r") as f:
        return json.load(f)


def save_profiles(profiles: Dict[str, Dict[str, str]]) -> None:
    """Persist all profiles to disk."""
    profiles_path = get_store_path() / PROFILES_FILE
    with profiles_path.open("w") as f:
        json.dump(profiles, f, indent=2)


def get_profile(name: str) -> Optional[Dict[str, str]]:
    """Retrieve a single profile by name. Returns None if not found."""
    return load_profiles().get(name)


def set_profile(name: str, variables: Dict[str, str]) -> None:
    """Create or overwrite a profile with the given variables."""
    profiles = load_profiles()
    profiles[name] = variables
    save_profiles(profiles)


def delete_profile(name: str) -> bool:
    """Delete a profile by name. Returns True if deleted, False if not found."""
    profiles = load_profiles()
    if name not in profiles:
        return False
    del profiles[name]
    save_profiles(profiles)
    return True


def list_profile_names() -> list:
    """Return a sorted list of all profile names."""
    return sorted(load_profiles().keys())
