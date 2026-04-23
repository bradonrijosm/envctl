"""Tests for envctl/cli_chain.py CLI commands."""
from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from envctl.cli_chain import cmd_chain


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    store.write_text("{}")
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: str(store))
    monkeypatch.setattr("envctl.env_chain.get_store_path", lambda: str(store))
    return store


@pytest.fixture()
def runner():
    return CliRunner()


def _seed(isolated_store, profiles: dict):
    isolated_store.write_text(json.dumps(profiles))


def test_chain_create_success(isolated_store, runner):
    _seed(isolated_store, {"dev": {"A": "1"}, "prod": {"A": "2"}})
    result = runner.invoke(cmd_chain, ["create", "mychain", "dev", "prod"])
    assert result.exit_code == 0
    assert "mychain" in result.output


def test_chain_create_missing_profile_fails(isolated_store, runner):
    _seed(isolated_store, {"dev": {"A": "1"}})
    result = runner.invoke(cmd_chain, ["create", "c", "dev", "ghost"])
    assert result.exit_code != 0
    assert "ghost" in result.output


def test_chain_delete_success(isolated_store, runner):
    _seed(isolated_store, {"dev": {"A": "1"}})
    runner.invoke(cmd_chain, ["create", "c", "dev"])
    result = runner.invoke(cmd_chain, ["delete", "c"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_chain_show_success(isolated_store, runner):
    _seed(isolated_store, {"dev": {"A": "1"}, "prod": {"A": "2"}})
    runner.invoke(cmd_chain, ["create", "c", "dev", "prod"])
    result = runner.invoke(cmd_chain, ["show", "c"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output


def test_chain_show_missing_fails(isolated_store, runner):
    _seed(isolated_store, {})
    result = runner.invoke(cmd_chain, ["show", "nope"])
    assert result.exit_code != 0


def test_chain_list_empty(isolated_store, runner):
    _seed(isolated_store, {})
    result = runner.invoke(cmd_chain, ["list"])
    assert result.exit_code == 0
    assert "No chains" in result.output


def test_chain_resolve_merges(isolated_store, runner):
    _seed(isolated_store, {
        "base": {"HOST": "localhost"},
        "top": {"HOST": "prod", "PORT": "80"},
    })
    runner.invoke(cmd_chain, ["create", "full", "base", "top"])
    result = runner.invoke(cmd_chain, ["resolve", "full"])
    assert result.exit_code == 0
    assert "HOST=prod" in result.output
    assert "PORT=80" in result.output
