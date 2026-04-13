"""Tests for envctl.tags."""

from __future__ import annotations

import pytest

from envctl.storage import save_profiles
from envctl.tags import (
    TagError,
    add_tag,
    find_by_tag,
    list_tags,
    remove_tag,
)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCTL_STORE_DIR", str(tmp_path))
    yield tmp_path


def _seed(profiles: dict):
    save_profiles(profiles)


# ---------------------------------------------------------------------------
# add_tag
# ---------------------------------------------------------------------------

def test_add_tag_success():
    _seed({"dev": {"DB": "localhost"}})
    tags = add_tag("dev", "backend")
    assert "backend" in tags


def test_add_tag_persists():
    _seed({"dev": {"DB": "localhost"}})
    add_tag("dev", "backend")
    assert "backend" in list_tags("dev")


def test_add_tag_duplicate_raises():
    _seed({"dev": {"DB": "localhost"}})
    add_tag("dev", "backend")
    with pytest.raises(TagError, match="already exists"):
        add_tag("dev", "backend")


def test_add_tag_missing_profile_raises():
    _seed({})
    with pytest.raises(TagError, match="does not exist"):
        add_tag("ghost", "mytag")


def test_add_tag_empty_string_raises():
    _seed({"dev": {}})
    with pytest.raises(TagError, match="must not be empty"):
        add_tag("dev", "   ")


# ---------------------------------------------------------------------------
# remove_tag
# ---------------------------------------------------------------------------

def test_remove_tag_success():
    _seed({"dev": {"__tags__": ["backend", "staging"]}})
    tags = remove_tag("dev", "backend")
    assert "backend" not in tags
    assert "staging" in tags


def test_remove_tag_not_present_raises():
    _seed({"dev": {"__tags__": ["backend"]}})
    with pytest.raises(TagError, match="not found"):
        remove_tag("dev", "frontend")


def test_remove_tag_missing_profile_raises():
    _seed({})
    with pytest.raises(TagError, match="does not exist"):
        remove_tag("ghost", "x")


# ---------------------------------------------------------------------------
# list_tags
# ---------------------------------------------------------------------------

def test_list_tags_empty():
    _seed({"dev": {"X": "1"}})
    assert list_tags("dev") == []


def test_list_tags_returns_all():
    _seed({"dev": {"__tags__": ["a", "b", "c"]}})
    assert sorted(list_tags("dev")) == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# find_by_tag
# ---------------------------------------------------------------------------

def test_find_by_tag_returns_matching_profiles():
    _seed({
        "dev": {"__tags__": ["backend"]},
        "prod": {"__tags__": ["backend", "live"]},
        "staging": {"__tags__": ["live"]},
    })
    result = find_by_tag("backend")
    assert set(result) == {"dev", "prod"}


def test_find_by_tag_no_matches():
    _seed({"dev": {"__tags__": ["backend"]}})
    assert find_by_tag("nonexistent") == []
