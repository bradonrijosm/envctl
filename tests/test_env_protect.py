"""Tests for envctl.env_protect."""

from __future__ import annotations

import json
import pytest

from envctl.env_protect import (
    ProtectError,
    protect_key,
    unprotect_key,
    list_protected,
    is_protected,
    assert_not_protected,
    _get_protect_path,
)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCTL_STORE_DIR", str(tmp_path))
    # Seed a profile so existence checks pass
    profiles_file = tmp_path / "profiles.json"
    profiles_file.write_text(json.dumps({"dev": {"API_KEY": "abc", "DEBUG": "1"}}))
    yield tmp_path


def test_protect_key_success():
    protect_key("dev", "API_KEY")
    assert is_protected("dev", "API_KEY")


def test_protect_key_persists(isolated_store):
    protect_key("dev", "DEBUG")
    raw = json.loads(_get_protect_path().read_text())
    assert "DEBUG" in raw["dev"]


def test_protect_key_duplicate_raises():
    protect_key("dev", "API_KEY")
    with pytest.raises(ProtectError, match="already protected"):
        protect_key("dev", "API_KEY")


def test_protect_key_missing_profile_raises():
    with pytest.raises(ProtectError, match="does not exist"):
        protect_key("ghost", "X")


def test_unprotect_key_success():
    protect_key("dev", "API_KEY")
    unprotect_key("dev", "API_KEY")
    assert not is_protected("dev", "API_KEY")


def test_unprotect_key_removes_profile_entry_when_empty(isolated_store):
    protect_key("dev", "API_KEY")
    unprotect_key("dev", "API_KEY")
    raw = json.loads(_get_protect_path().read_text())
    assert "dev" not in raw


def test_unprotect_key_not_protected_raises():
    with pytest.raises(ProtectError, match="not protected"):
        unprotect_key("dev", "API_KEY")


def test_list_protected_sorted():
    protect_key("dev", "Z_VAR")
    protect_key("dev", "A_VAR")
    assert list_protected("dev") == ["A_VAR", "Z_VAR"]


def test_list_protected_empty_profile():
    assert list_protected("dev") == []


def test_is_protected_true():
    protect_key("dev", "API_KEY")
    assert is_protected("dev", "API_KEY") is True


def test_is_protected_false():
    assert is_protected("dev", "API_KEY") is False


def test_assert_not_protected_raises_when_protected():
    protect_key("dev", "API_KEY")
    with pytest.raises(ProtectError, match="cannot be modified"):
        assert_not_protected("dev", "API_KEY")


def test_assert_not_protected_passes_when_clear():
    assert_not_protected("dev", "API_KEY")  # should not raise
