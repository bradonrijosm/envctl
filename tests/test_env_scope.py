"""Tests for envctl.env_scope."""

from __future__ import annotations

import json
import pytest

from envctl.env_scope import (
    ScopeError,
    bind_scope,
    list_scopes,
    resolve_scope,
    unbind_scope,
    _get_scope_path,
)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store_file = tmp_path / "profiles.json"
    store_file.write_text(json.dumps({}))
    monkeypatch.setattr("envctl.env_scope.get_store_path", lambda: store_file)
    monkeypatch.setattr("envctl.env_scope._get_scope_path",
                        lambda: tmp_path / "scopes.json")
    yield tmp_path


def _seed_profile(name: str, isolated_store) -> None:
    store_file = isolated_store / "profiles.json"
    data = json.loads(store_file.read_text())
    data[name] = {"KEY": "val"}
    store_file.write_text(json.dumps(data))


def _patch_get(monkeypatch, isolated_store):
    store_file = isolated_store / "profiles.json"

    def _fake_get(name):
        data = json.loads(store_file.read_text())
        return data.get(name)

    monkeypatch.setattr("envctl.env_scope.get_profile", _fake_get)


def test_bind_scope_success(monkeypatch, isolated_store):
    _seed_profile("dev", isolated_store)
    _patch_get(monkeypatch, isolated_store)
    bind_scope("/home/user/project", "dev")
    assert resolve_scope("/home/user/project") == "dev"


def test_bind_scope_missing_profile_raises(monkeypatch, isolated_store):
    _patch_get(monkeypatch, isolated_store)
    with pytest.raises(ScopeError, match="does not exist"):
        bind_scope("/home/user/project", "nonexistent")


def test_bind_scope_overwrites_existing(monkeypatch, isolated_store):
    _seed_profile("dev", isolated_store)
    _seed_profile("prod", isolated_store)
    _patch_get(monkeypatch, isolated_store)
    bind_scope("myproject", "dev")
    bind_scope("myproject", "prod")
    assert resolve_scope("myproject") == "prod"


def test_unbind_scope_success(monkeypatch, isolated_store):
    _seed_profile("dev", isolated_store)
    _patch_get(monkeypatch, isolated_store)
    bind_scope("proj", "dev")
    unbind_scope("proj")
    assert resolve_scope("proj") is None


def test_unbind_scope_not_bound_raises(isolated_store):
    with pytest.raises(ScopeError, match="not bound"):
        unbind_scope("ghost")


def test_resolve_scope_missing_returns_none(isolated_store):
    assert resolve_scope("unknown") is None


def test_list_scopes_empty(isolated_store):
    assert list_scopes() == []


def test_list_scopes_sorted(monkeypatch, isolated_store):
    _seed_profile("dev", isolated_store)
    _seed_profile("prod", isolated_store)
    _patch_get(monkeypatch, isolated_store)
    bind_scope("z_scope", "prod")
    bind_scope("a_scope", "dev")
    result = list_scopes()
    assert result[0]["scope"] == "a_scope"
    assert result[1]["scope"] == "z_scope"
