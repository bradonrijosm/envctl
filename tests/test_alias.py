"""Tests for envctl.alias."""

from __future__ import annotations

import json
import pytest

from envctl.alias import (
    AliasError,
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    rename_alias,
    _get_alias_path,
)
from envctl.storage import set_profile


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store_file = tmp_path / "profiles.json"
    store_file.write_text("{}")
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store_file)
    monkeypatch.setattr("envctl.alias.get_store_path", lambda: store_file)
    yield tmp_path


def _seed(name: str, vars: dict | None = None) -> None:
    set_profile(name, vars or {"KEY": "val"})


def test_add_alias_success(isolated_store):
    _seed("production")
    add_alias("prod", "production")
    assert resolve_alias("prod") == "production"


def test_add_alias_persists(isolated_store):
    _seed("staging")
    add_alias("stg", "staging")
    raw = json.loads(_get_alias_path().read_text())
    assert raw["stg"] == "staging"


def test_add_alias_missing_profile_raises(isolated_store):
    with pytest.raises(AliasError, match="does not exist"):
        add_alias("ghost", "nonexistent")


def test_add_alias_duplicate_raises(isolated_store):
    _seed("production")
    add_alias("prod", "production")
    with pytest.raises(AliasError, match="already exists"):
        add_alias("prod", "production")


def test_remove_alias_success(isolated_store):
    _seed("production")
    add_alias("prod", "production")
    remove_alias("prod")
    assert resolve_alias("prod") is None


def test_remove_alias_missing_raises(isolated_store):
    with pytest.raises(AliasError, match="does not exist"):
        remove_alias("nope")


def test_resolve_alias_missing_returns_none(isolated_store):
    assert resolve_alias("unknown") is None


def test_list_aliases_empty(isolated_store):
    assert list_aliases() == {}


def test_list_aliases_returns_all(isolated_store):
    _seed("dev")
    _seed("prod")
    add_alias("d", "dev")
    add_alias("p", "prod")
    result = list_aliases()
    assert result == {"d": "dev", "p": "prod"}


def test_rename_alias_success(isolated_store):
    _seed("production")
    add_alias("prod", "production")
    rename_alias("prod", "prd")
    assert resolve_alias("prd") == "production"
    assert resolve_alias("prod") is None


def test_rename_alias_missing_raises(isolated_store):
    with pytest.raises(AliasError, match="does not exist"):
        rename_alias("ghost", "specter")


def test_rename_alias_dest_exists_raises(isolated_store):
    _seed("production")
    _seed("staging")
    add_alias("prod", "production")
    add_alias("stg", "staging")
    with pytest.raises(AliasError, match="already exists"):
        rename_alias("prod", "stg")
