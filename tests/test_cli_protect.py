"""Tests for envctl.cli_protect CLI commands."""

from __future__ import annotations

import json
import pytest
from click.testing import CliRunner

from envctl.cli_protect import cmd_protect


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCTL_STORE_DIR", str(tmp_path))
    profiles_file = tmp_path / "profiles.json"
    profiles_file.write_text(json.dumps({"dev": {"API_KEY": "abc", "DEBUG": "1"}}))
    yield tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


def test_protect_add_success(isolated_store, runner):
    result = runner.invoke(cmd_protect, ["add", "dev", "API_KEY"])
    assert result.exit_code == 0
    assert "protected" in result.output


def test_protect_add_missing_profile_fails(isolated_store, runner):
    result = runner.invoke(cmd_protect, ["add", "ghost", "X"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_protect_add_duplicate_fails(isolated_store, runner):
    runner.invoke(cmd_protect, ["add", "dev", "API_KEY"])
    result = runner.invoke(cmd_protect, ["add", "dev", "API_KEY"])
    assert result.exit_code != 0
    assert "already protected" in result.output


def test_protect_remove_success(isolated_store, runner):
    runner.invoke(cmd_protect, ["add", "dev", "API_KEY"])
    result = runner.invoke(cmd_protect, ["remove", "dev", "API_KEY"])
    assert result.exit_code == 0
    assert "no longer protected" in result.output


def test_protect_remove_not_protected_fails(isolated_store, runner):
    result = runner.invoke(cmd_protect, ["remove", "dev", "API_KEY"])
    assert result.exit_code != 0
    assert "not protected" in result.output


def test_protect_list_shows_keys(isolated_store, runner):
    runner.invoke(cmd_protect, ["add", "dev", "API_KEY"])
    runner.invoke(cmd_protect, ["add", "dev", "DEBUG"])
    result = runner.invoke(cmd_protect, ["list", "dev"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DEBUG" in result.output


def test_protect_list_empty(isolated_store, runner):
    result = runner.invoke(cmd_protect, ["list", "dev"])
    assert result.exit_code == 0
    assert "No protected keys" in result.output


def test_protect_status_protected(isolated_store, runner):
    runner.invoke(cmd_protect, ["add", "dev", "API_KEY"])
    result = runner.invoke(cmd_protect, ["status", "dev", "API_KEY"])
    assert result.exit_code == 0
    assert "PROTECTED" in result.output


def test_protect_status_not_protected(isolated_store, runner):
    result = runner.invoke(cmd_protect, ["status", "dev", "API_KEY"])
    assert result.exit_code == 0
    assert "not protected" in result.output
