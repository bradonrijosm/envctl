"""Tests for envctl.inherit and envctl.cli_inherit."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envctl.inherit import InheritError, inherit_profile, rebase_profile
from envctl.storage import get_profile, set_profile, load_profiles
from envctl.cli_inherit import cmd_inherit


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "store.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.inherit.get_profile",
        lambda name, **kw: get_profile(name, store_path=store))
    monkeypatch.setattr("envctl.inherit.load_profiles",
        lambda **kw: load_profiles(store_path=store))
    monkeypatch.setattr("envctl.inherit.set_profile",
        lambda name, vars, **kw: set_profile(name, vars, store_path=store))
    return store


def _seed(store, name, vars_):
    set_profile(name, vars_, store_path=store)


# --- inherit_profile ---

def test_inherit_creates_derived_with_base_vars(isolated_store):
    _seed(isolated_store, "base", {"A": "1", "B": "2"})
    result = inherit_profile("base", "derived", {}, store_path=isolated_store)
    assert result == {"A": "1", "B": "2"}


def test_inherit_overrides_replace_base_keys(isolated_store):
    _seed(isolated_store, "base", {"A": "1", "B": "2"})
    result = inherit_profile("base", "derived", {"B": "99"}, store_path=isolated_store)
    assert result["B"] == "99"
    assert result["A"] == "1"


def test_inherit_overrides_add_new_keys(isolated_store):
    _seed(isolated_store, "base", {"A": "1"})
    result = inherit_profile("base", "derived", {"NEW": "x"}, store_path=isolated_store)
    assert result["NEW"] == "x"


def test_inherit_persists_to_store(isolated_store):
    _seed(isolated_store, "base", {"X": "hello"})
    inherit_profile("base", "child", {}, store_path=isolated_store)
    assert get_profile("child", store_path=isolated_store) == {"X": "hello"}


def test_inherit_base_unchanged(isolated_store):
    _seed(isolated_store, "base", {"A": "1"})
    inherit_profile("base", "child", {"A": "99"}, store_path=isolated_store)
    assert get_profile("base", store_path=isolated_store) == {"A": "1"}


def test_inherit_missing_base_raises(isolated_store):
    with pytest.raises(InheritError, match="does not exist"):
        inherit_profile("ghost", "child", {}, store_path=isolated_store)


def test_inherit_duplicate_derived_raises(isolated_store):
    _seed(isolated_store, "base", {"A": "1"})
    _seed(isolated_store, "child", {"A": "2"})
    with pytest.raises(InheritError, match="already exists"):
        inherit_profile("base", "child", {}, store_path=isolated_store)


# --- rebase_profile ---

def test_rebase_merges_new_base(isolated_store):
    _seed(isolated_store, "base2", {"A": "10", "C": "30"})
    _seed(isolated_store, "child", {"A": "99", "B": "20"})
    result = rebase_profile("child", "base2", store_path=isolated_store)
    assert result["A"] == "99"   # child override wins
    assert result["C"] == "30"   # new base key added
    assert result["B"] == "20"   # child-only key preserved


def test_rebase_missing_new_base_raises(isolated_store):
    _seed(isolated_store, "child", {"A": "1"})
    with pytest.raises(InheritError, match="does not exist"):
        rebase_profile("child", "ghost", store_path=isolated_store)


def test_rebase_missing_profile_raises(isolated_store):
    _seed(isolated_store, "base", {"A": "1"})
    with pytest.raises(InheritError, match="does not exist"):
        rebase_profile("ghost", "base", store_path=isolated_store)


# --- CLI ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_inherit_create_success(runner, isolated_store):
    _seed(isolated_store, "prod", {"DB": "prod-db"})
    result = runner.invoke(cmd_inherit, ["create", "prod", "staging", "--set", "DB=staging-db"])
    assert result.exit_code == 0
    assert "staging" in result.output


def test_cli_inherit_create_bad_pair(runner, isolated_store):
    _seed(isolated_store, "prod", {"DB": "x"})
    result = runner.invoke(cmd_inherit, ["create", "prod", "stg", "--set", "NODOT"])
    assert result.exit_code != 0


def test_cli_inherit_create_missing_base(runner, isolated_store):
    result = runner.invoke(cmd_inherit, ["create", "ghost", "child"])
    assert result.exit_code != 0
    assert "Error" in result.output
