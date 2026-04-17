"""TTL (time-to-live) expiry for environment profiles."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from envctl.storage import get_store_path, get_profile


class TTLError(Exception):
    pass


def _get_ttl_path() -> Path:
    return get_store_path().parent / "ttl.json"


def _load_ttl() -> dict:
    p = _get_ttl_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ttl(data: dict) -> None:
    _get_ttl_path().write_text(json.dumps(data, indent=2))


def set_ttl(profile: str, seconds: int) -> None:
    """Set a TTL (in seconds from now) for a profile."""
    if get_profile(profile) is None:
        raise TTLError(f"Profile '{profile}' does not exist.")
    if seconds <= 0:
        raise TTLError("TTL must be a positive integer.")
    data = _load_ttl()
    data[profile] = {"expires_at": time.time() + seconds}
    _save_ttl(data)


def get_ttl(profile: str) -> Optional[float]:
    """Return the expiry timestamp for a profile, or None if not set."""
    return _load_ttl().get(profile, {}).get("expires_at")


def remove_ttl(profile: str) -> None:
    """Remove the TTL for a profile."""
    data = _load_ttl()
    if profile not in data:
        raise TTLError(f"No TTL set for profile '{profile}'.")
    del data[profile]
    _save_ttl(data)


def is_expired(profile: str) -> bool:
    """Return True if the profile has a TTL and it has passed."""
    expires_at = get_ttl(profile)
    if expires_at is None:
        return False
    return time.time() >= expires_at


def list_ttls() -> list[dict]:
    """Return all TTL entries with remaining seconds."""
    now = time.time()
    result = []
    for profile, meta in _load_ttl().items():
        expires_at = meta.get("expires_at", 0)
        remaining = max(0.0, expires_at - now)
        result.append({
            "profile": profile,
            "expires_at": expires_at,
            "remaining_seconds": remaining,
            "expired": now >= expires_at,
        })
    return result
