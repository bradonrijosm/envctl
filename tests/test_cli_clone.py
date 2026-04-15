"""Tests for envctl.cli_clone."""

from __future__ import annotations

import json
import pytest
from click.testing import CliRunner

from envctl.cli_clone import cmd_clone


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    return store


@pytest.fixture()
def runner():
    return CliRunner()


def _seed(isolated_store, profiles: dict) -> None:
    isolated_store.write_text(json.dumps(profiles))


def test_clone_copy_success(isolated_store, runner):
    _seed(isolated_store, {"prod": {"HOST": "prod.example.com"}})
    result = runner.invoke(cmd_clone, ["copy", "prod", "staging"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "staging" in result.output


def test_clone_copy_with_override(isolated_store, runner):
    _seed(isolated_store, {"prod": {"HOST": "prod.example.com", "PORT": "443"}})
    result = runner.invoke(
        cmd_clone, ["copy", "prod", "staging", "--set", "HOST=staging.example.com"]
    )
    assert result.exit_code == 0
    data = json.loads(isolated_store.read_text())
    assert data["staging"]["HOST"] == "staging.example.com"
    assert data["staging"]["PORT"] == "443"


def test_clone_copy_missing_source(isolated_store, runner):
    _seed(isolated_store, {})
    result = runner.invoke(cmd_clone, ["copy", "ghost", "copy"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_clone_copy_bad_override_format(isolated_store, runner):
    _seed(isolated_store, {"prod": {"A": "1"}})
    result = runner.invoke(cmd_clone, ["copy", "prod", "staging", "--set", "NOEQUALS"])
    assert result.exit_code != 0


def test_clone_prefix_success(isolated_store, runner):
    _seed(isolated_store, {"prod": {"HOST": "h", "PORT": "80"}})
    result = runner.invoke(cmd_clone, ["prefix", "prod", "prefixed", "PROD_"])
    assert result.exit_code == 0
    data = json.loads(isolated_store.read_text())
    assert "PROD_HOST" in data["prefixed"]
    assert "PROD_PORT" in data["prefixed"]


def test_clone_prefix_missing_source(isolated_store, runner):
    _seed(isolated_store, {})
    result = runner.invoke(cmd_clone, ["prefix", "ghost", "copy", "X_"])
    assert result.exit_code != 0
    assert "does not exist" in result.output
