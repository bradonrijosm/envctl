"""Tests for envctl.env_set — bulk_set and bulk_unset."""

from __future__ import annotations

import pytest

from envctl.env_set import EnvSetError, bulk_set, bulk_unset
from envctl.storage import get_profile, set_profile


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCTL_STORE_DIR", str(tmp_path))
    yield tmp_path


def _seed(name: str, vars: dict) -> None:
    set_profile(name, vars)


# --- bulk_set ---

def test_bulk_set_adds_new_keys():
    _seed("dev", {"A": "1"})
    result = bulk_set("dev", {"B": "2", "C": "3"})
    assert result["B"] == "2"
    assert result["C"] == "3"
    assert result["A"] == "1"


def test_bulk_set_persists_to_store():
    _seed("dev", {})
    bulk_set("dev", {"X": "hello"})
    assert get_profile("dev") == {"X": "hello"}


def test_bulk_set_overwrite_default_replaces():
    _seed("dev", {"KEY": "old"})
    bulk_set("dev", {"KEY": "new"})
    assert get_profile("dev")["KEY"] == "new"


def test_bulk_set_no_overwrite_keeps_existing():
    _seed("dev", {"KEY": "original"})
    result = bulk_set("dev", {"KEY": "replaced", "NEW": "val"}, overwrite=False)
    assert result["KEY"] == "original"
    assert result["NEW"] == "val"


def test_bulk_set_dry_run_does_not_persist():
    _seed("dev", {"A": "1"})
    bulk_set("dev", {"A": "999"}, dry_run=True)
    assert get_profile("dev")["A"] == "1"


def test_bulk_set_missing_profile_raises():
    with pytest.raises(EnvSetError, match="does not exist"):
        bulk_set("ghost", {"X": "1"})


def test_bulk_set_invalid_var_name_raises():
    _seed("dev", {})
    with pytest.raises(EnvSetError, match="Invalid variable name"):
        bulk_set("dev", {"123BAD": "v"})


def test_bulk_set_invalid_profile_name_raises():
    with pytest.raises(EnvSetError, match="Invalid profile name"):
        bulk_set("bad name!", {"X": "1"})


# --- bulk_unset ---

def test_bulk_unset_removes_keys():
    _seed("dev", {"A": "1", "B": "2", "C": "3"})
    result = bulk_unset("dev", ["A", "C"])
    assert "A" not in result
    assert "C" not in result
    assert result["B"] == "2"


def test_bulk_unset_persists():
    _seed("dev", {"A": "1", "B": "2"})
    bulk_unset("dev", ["A"])
    assert "A" not in get_profile("dev")


def test_bulk_unset_missing_key_silently_ignored():
    _seed("dev", {"A": "1"})
    result = bulk_unset("dev", ["NONEXISTENT"])
    assert result == {"A": "1"}


def test_bulk_unset_dry_run_does_not_persist():
    _seed("dev", {"A": "1", "B": "2"})
    bulk_unset("dev", ["A"], dry_run=True)
    assert "A" in get_profile("dev")


def test_bulk_unset_missing_profile_raises():
    with pytest.raises(EnvSetError, match="does not exist"):
        bulk_unset("ghost", ["X"])
