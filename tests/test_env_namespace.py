"""Tests for envctl.env_namespace."""

from __future__ import annotations

import pytest

from envctl.env_namespace import (
    NamespaceError,
    delete_namespace,
    get_namespace,
    list_namespaces,
    set_namespace,
)
from envctl.storage import save_profiles


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    return store


def _seed(profiles: dict):
    save_profiles(profiles)


# --- list_namespaces ---

def test_list_namespaces_returns_sorted(isolated_store):
    _seed({"dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"}})
    result = list_namespaces("dev")
    assert result == ["APP", "DB"]


def test_list_namespaces_empty_profile(isolated_store):
    _seed({"dev": {"NOPREFIX": "val"}})
    result = list_namespaces("dev")
    assert result == []


def test_list_namespaces_missing_profile_raises(isolated_store):
    _seed({})
    with pytest.raises(NamespaceError, match="not found"):
        list_namespaces("ghost")


# --- get_namespace ---

def test_get_namespace_returns_matching_keys(isolated_store):
    _seed({"dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"}})
    result = get_namespace("dev", "DB")
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_get_namespace_no_match_returns_empty(isolated_store):
    _seed({"dev": {"APP_ENV": "dev"}})
    assert get_namespace("dev", "DB") == {}


def test_get_namespace_missing_profile_raises(isolated_store):
    _seed({})
    with pytest.raises(NamespaceError):
        get_namespace("ghost", "DB")


# --- set_namespace ---

def test_set_namespace_prefixes_bare_keys(isolated_store):
    _seed({"dev": {}})
    updated = set_namespace("dev", "DB", {"HOST": "localhost", "PORT": "5432"})
    assert "DB_HOST" in updated
    assert "DB_PORT" in updated


def test_set_namespace_already_prefixed_key_stored_as_is(isolated_store):
    _seed({"dev": {}})
    updated = set_namespace("dev", "DB", {"DB_HOST": "localhost"})
    assert "DB_HOST" in updated
    assert "DB_DB_HOST" not in updated


def test_set_namespace_no_overwrite_keeps_existing(isolated_store):
    _seed({"dev": {"DB_HOST": "original"}})
    set_namespace("dev", "DB", {"HOST": "new"}, overwrite=False)
    result = get_namespace("dev", "DB")
    assert result["DB_HOST"] == "original"


def test_set_namespace_empty_namespace_raises(isolated_store):
    _seed({"dev": {}})
    with pytest.raises(NamespaceError, match="non-empty"):
        set_namespace("dev", "", {"FOO": "bar"})


# --- delete_namespace ---

def test_delete_namespace_removes_keys(isolated_store):
    _seed({"dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"}})
    removed = delete_namespace("dev", "DB")
    assert set(removed) == {"DB_HOST", "DB_PORT"}
    remaining = get_namespace("dev", "DB")
    assert remaining == {}


def test_delete_namespace_leaves_other_keys(isolated_store):
    _seed({"dev": {"DB_HOST": "localhost", "APP_ENV": "dev"}})
    delete_namespace("dev", "DB")
    result = get_namespace("dev", "APP")
    assert result == {"APP_ENV": "dev"}


def test_delete_namespace_missing_profile_raises(isolated_store):
    _seed({})
    with pytest.raises(NamespaceError):
        delete_namespace("ghost", "DB")
