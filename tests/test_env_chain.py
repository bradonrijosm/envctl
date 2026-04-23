"""Tests for envctl/env_chain.py."""
from __future__ import annotations

import json
import pathlib

import pytest

from envctl.env_chain import (
    ChainError,
    create_chain,
    delete_chain,
    get_chain,
    list_chains,
    resolve_chain,
)


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    store.write_text("{}")
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: str(store))
    monkeypatch.setattr("envctl.env_chain.get_store_path", lambda: str(store))
    return store


def _seed(isolated_store, profiles: dict):
    isolated_store.write_text(json.dumps(profiles))


# ---------------------------------------------------------------------------
# create_chain
# ---------------------------------------------------------------------------

def test_create_chain_success(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}, "prod": {"B": "2"}})
    create_chain("mychain", ["dev", "prod"])
    assert get_chain("mychain") == ["dev", "prod"]


def test_create_chain_missing_profile_raises(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    with pytest.raises(ChainError, match="ghost"):
        create_chain("bad", ["dev", "ghost"])


def test_create_chain_empty_profiles_raises(isolated_store):
    _seed(isolated_store, {})
    with pytest.raises(ChainError, match="at least one"):
        create_chain("empty", [])


def test_create_chain_duplicate_raises(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    create_chain("c", ["dev"])
    with pytest.raises(ChainError, match="already exists"):
        create_chain("c", ["dev"])


# ---------------------------------------------------------------------------
# delete_chain
# ---------------------------------------------------------------------------

def test_delete_chain_success(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    create_chain("c", ["dev"])
    delete_chain("c")
    assert get_chain("c") is None


def test_delete_chain_missing_raises(isolated_store):
    _seed(isolated_store, {})
    with pytest.raises(ChainError, match="does not exist"):
        delete_chain("nope")


# ---------------------------------------------------------------------------
# list_chains
# ---------------------------------------------------------------------------

def test_list_chains_returns_all(isolated_store):
    _seed(isolated_store, {"a": {"X": "1"}, "b": {"Y": "2"}})
    create_chain("c1", ["a"])
    create_chain("c2", ["a", "b"])
    chains = list_chains()
    assert set(chains.keys()) == {"c1", "c2"}


# ---------------------------------------------------------------------------
# resolve_chain
# ---------------------------------------------------------------------------

def test_resolve_chain_merges_in_order(isolated_store):
    _seed(isolated_store, {
        "base": {"HOST": "localhost", "PORT": "5432"},
        "override": {"HOST": "prod.db", "EXTRA": "yes"},
    })
    create_chain("full", ["base", "override"])
    result = resolve_chain("full")
    assert result["HOST"] == "prod.db"   # override wins
    assert result["PORT"] == "5432"       # base value kept
    assert result["EXTRA"] == "yes"       # override-only key present


def test_resolve_chain_missing_chain_raises(isolated_store):
    _seed(isolated_store, {})
    with pytest.raises(ChainError, match="does not exist"):
        resolve_chain("ghost")
