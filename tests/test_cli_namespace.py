"""CLI tests for the namespace commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envctl.cli_namespace import cmd_namespace
from envctl.storage import save_profiles


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    return store


@pytest.fixture()
def runner():
    return CliRunner()


def _seed(profiles: dict):
    save_profiles(profiles)


def test_ns_list_success(isolated_store, runner):
    _seed({"dev": {"DB_HOST": "localhost", "APP_ENV": "dev"}})
    result = runner.invoke(cmd_namespace, ["list", "dev"])
    assert result.exit_code == 0
    assert "APP" in result.output
    assert "DB" in result.output


def test_ns_list_empty(isolated_store, runner):
    _seed({"dev": {"NOPREFIX": "val"}})
    result = runner.invoke(cmd_namespace, ["list", "dev"])
    assert result.exit_code == 0
    assert "No namespaces" in result.output


def test_ns_list_missing_profile(isolated_store, runner):
    _seed({})
    result = runner.invoke(cmd_namespace, ["list", "ghost"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "Error" in result.output


def test_ns_get_success(isolated_store, runner):
    _seed({"dev": {"DB_HOST": "localhost", "DB_PORT": "5432"}})
    result = runner.invoke(cmd_namespace, ["get", "dev", "DB"])
    assert result.exit_code == 0
    assert "DB_HOST=localhost" in result.output
    assert "DB_PORT=5432" in result.output


def test_ns_get_no_match(isolated_store, runner):
    _seed({"dev": {"APP_ENV": "dev"}})
    result = runner.invoke(cmd_namespace, ["get", "dev", "DB"])
    assert result.exit_code == 0
    assert "No variables" in result.output


def test_ns_set_success(isolated_store, runner):
    _seed({"dev": {}})
    result = runner.invoke(cmd_namespace, ["set", "dev", "DB", "HOST=localhost", "PORT=5432"])
    assert result.exit_code == 0
    assert "2 variable(s)" in result.output


def test_ns_set_invalid_pair(isolated_store, runner):
    _seed({"dev": {}})
    result = runner.invoke(cmd_namespace, ["set", "dev", "DB", "INVALID"])
    assert result.exit_code != 0


def test_ns_delete_success(isolated_store, runner):
    _seed({"dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"}})
    result = runner.invoke(cmd_namespace, ["delete", "dev", "DB"])
    assert result.exit_code == 0
    assert "2 variable(s)" in result.output
