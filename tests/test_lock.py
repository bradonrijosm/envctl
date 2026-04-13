"""Tests for envctl.lock."""

from __future__ import annotations

import pytest

from envctl.lock import (
    LockError,
    assert_unlocked,
    is_locked,
    list_locked,
    lock_profile,
    unlock_profile,
)
from envctl.storage import load_profiles, save_profiles


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCTL_STORE_DIR", str(tmp_path))
    return str(tmp_path)


def _seed(store_dir: str, *names: str) -> None:
    profiles = load_profiles(store_dir)
    for name in names:
        profiles[name] = {"VAR": "value"}
    save_profiles(profiles, store_dir)


def test_lock_profile_success(isolated_store):
    _seed(isolated_store, "prod")
    lock_profile("prod", isolated_store)
    assert is_locked("prod", isolated_store) is True


def test_lock_profile_persists(isolated_store):
    _seed(isolated_store, "prod")
    lock_profile("prod", isolated_store)
    # reload to confirm persistence
    assert "prod" in list_locked(isolated_store)


def test_lock_nonexistent_profile_raises(isolated_store):
    with pytest.raises(LockError, match="does not exist"):
        lock_profile("ghost", isolated_store)


def test_lock_already_locked_raises(isolated_store):
    _seed(isolated_store, "staging")
    lock_profile("staging", isolated_store)
    with pytest.raises(LockError, match="already locked"):
        lock_profile("staging", isolated_store)


def test_unlock_profile_success(isolated_store):
    _seed(isolated_store, "dev")
    lock_profile("dev", isolated_store)
    unlock_profile("dev", isolated_store)
    assert is_locked("dev", isolated_store) is False


def test_unlock_not_locked_raises(isolated_store):
    _seed(isolated_store, "dev")
    with pytest.raises(LockError, match="not locked"):
        unlock_profile("dev", isolated_store)


def test_list_locked_returns_sorted(isolated_store):
    _seed(isolated_store, "alpha", "beta", "gamma")
    lock_profile("gamma", isolated_store)
    lock_profile("alpha", isolated_store)
    assert list_locked(isolated_store) == ["alpha", "gamma"]


def test_list_locked_empty(isolated_store):
    assert list_locked(isolated_store) == []


def test_assert_unlocked_passes_for_unlocked(isolated_store):
    _seed(isolated_store, "dev")
    assert_unlocked("dev", isolated_store)  # should not raise


def test_assert_unlocked_raises_for_locked(isolated_store):
    _seed(isolated_store, "prod")
    lock_profile("prod", isolated_store)
    with pytest.raises(LockError, match="Unlock it first"):
        assert_unlocked("prod", isolated_store)
