"""Tests for envctl.group."""
import json
import pytest

from envctl.group import (
    GroupError,
    add_profile_to_group,
    create_group,
    delete_group,
    get_group_members,
    list_groups,
    remove_profile_from_group,
)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "store.json"
    store.write_text(json.dumps({"dev": {"KEY": "val"}, "prod": {"KEY": "prod_val"}}))
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.group.get_store_path", lambda: store)
    yield store


def test_create_group_success():
    create_group("backend")
    assert "backend" in list_groups()


def test_create_group_duplicate_raises():
    create_group("backend")
    with pytest.raises(GroupError, match="already exists"):
        create_group("backend")


def test_delete_group_success():
    create_group("backend")
    delete_group("backend")
    assert "backend" not in list_groups()


def test_delete_group_missing_raises():
    with pytest.raises(GroupError, match="does not exist"):
        delete_group("nonexistent")


def test_add_profile_to_group_success():
    create_group("backend")
    add_profile_to_group("backend", "dev")
    assert "dev" in get_group_members("backend")


def test_add_profile_to_group_missing_profile_raises():
    create_group("backend")
    with pytest.raises(GroupError, match="Profile 'ghost' does not exist"):
        add_profile_to_group("backend", "ghost")


def test_add_profile_to_group_missing_group_raises():
    with pytest.raises(GroupError, match="Group 'nogroup' does not exist"):
        add_profile_to_group("nogroup", "dev")


def test_add_profile_duplicate_raises():
    create_group("backend")
    add_profile_to_group("backend", "dev")
    with pytest.raises(GroupError, match="already in group"):
        add_profile_to_group("backend", "dev")


def test_remove_profile_from_group_success():
    create_group("backend")
    add_profile_to_group("backend", "dev")
    remove_profile_from_group("backend", "dev")
    assert "dev" not in get_group_members("backend")


def test_remove_profile_not_in_group_raises():
    create_group("backend")
    with pytest.raises(GroupError, match="not in group"):
        remove_profile_from_group("backend", "dev")


def test_list_groups_empty():
    assert list_groups() == {}


def test_list_groups_multiple():
    create_group("g1")
    create_group("g2")
    add_profile_to_group("g1", "dev")
    groups = list_groups()
    assert set(groups.keys()) == {"g1", "g2"}
    assert groups["g1"] == ["dev"]


def test_get_group_members_missing_raises():
    with pytest.raises(GroupError, match="does not exist"):
        get_group_members("missing")
