"""Tests for envctl.profiles business logic."""

import pytest

import envctl.storage as storage
from envctl.profiles import (
    ProfileError,
    create_profile,
    export_shell,
    get_profile,
    list_profiles,
    remove_profile,
    update_profile,
)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCTL_HOME", str(tmp_path))
    yield


def test_create_profile_success():
    create_profile("dev", {"DEBUG": "1"})
    assert storage.get_profile("dev") == {"DEBUG": "1"}


def test_create_profile_duplicate_raises():
    create_profile("dev", {"DEBUG": "1"})
    with pytest.raises(ProfileError, match="already exists"):
        create_profile("dev", {"DEBUG": "0"})


def test_update_profile_replaces_variables():
    create_profile("dev", {"A": "1", "B": "2"})
    update_profile("dev", {"C": "3"})
    assert get_profile("dev") == {"C": "3"}


def test_update_profile_merge():
    create_profile("dev", {"A": "1", "B": "2"})
    update_profile("dev", {"B": "99", "C": "3"}, merge=True)
    assert get_profile("dev") == {"A": "1", "B": "99", "C": "3"}


def test_update_missing_profile_raises():
    with pytest.raises(ProfileError, match="does not exist"):
        update_profile("ghost", {})


def test_remove_profile_success():
    create_profile("tmp", {})
    remove_profile("tmp")
    assert storage.get_profile("tmp") is None


def test_remove_missing_profile_raises():
    with pytest.raises(ProfileError, match="does not exist"):
        remove_profile("nobody")


def test_list_profiles():
    create_profile("b", {})
    create_profile("a", {})
    assert list_profiles() == ["a", "b"]


def test_export_shell_format():
    create_profile("ci", {"TOKEN": "abc123", "ENV": "ci"})
    output = export_shell("ci")
    assert "export ENV='ci'" in output
    assert "export TOKEN='abc123'" in output
