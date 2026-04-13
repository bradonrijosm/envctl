"""Profile locking — prevent accidental modification of profiles."""

from __future__ import annotations

from typing import List

from envctl.storage import get_store_path, load_profiles, save_profiles

_LOCK_KEY = "__locked_profiles__"


class LockError(Exception):
    """Raised when a lock operation fails."""


def _get_locks(store_dir: str | None = None) -> List[str]:
    """Return the list of currently locked profile names."""
    profiles = load_profiles(store_dir)
    return profiles.get(_LOCK_KEY, [])


def _save_locks(locks: List[str], store_dir: str | None = None) -> None:
    profiles = load_profiles(store_dir)
    profiles[_LOCK_KEY] = locks
    save_profiles(profiles, store_dir)


def lock_profile(name: str, store_dir: str | None = None) -> None:
    """Lock *name* so it cannot be modified or deleted."""
    profiles = load_profiles(store_dir)
    if name not in profiles:
        raise LockError(f"Profile '{name}' does not exist.")
    locks = _get_locks(store_dir)
    if name in locks:
        raise LockError(f"Profile '{name}' is already locked.")
    locks.append(name)
    _save_locks(locks, store_dir)


def unlock_profile(name: str, store_dir: str | None = None) -> None:
    """Remove the lock from *name*."""
    locks = _get_locks(store_dir)
    if name not in locks:
        raise LockError(f"Profile '{name}' is not locked.")
    locks.remove(name)
    _save_locks(locks, store_dir)


def is_locked(name: str, store_dir: str | None = None) -> bool:
    """Return True if *name* is locked."""
    return name in _get_locks(store_dir)


def assert_unlocked(name: str, store_dir: str | None = None) -> None:
    """Raise *LockError* if *name* is locked."""
    if is_locked(name, store_dir):
        raise LockError(
            f"Profile '{name}' is locked. Unlock it first with `envctl lock unlock {name}`."
        )


def list_locked(store_dir: str | None = None) -> List[str]:
    """Return a sorted list of all locked profile names."""
    return sorted(_get_locks(store_dir))
