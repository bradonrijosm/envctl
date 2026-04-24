"""Tests for envctl.cli_freeze CLI commands."""

from __future__ import annotations

import json
import pytest
from click.testing import CliRunner

from envctl.cli_freeze import cmd_freeze


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    store.write_text(json.dumps({"dev": {"KEY": "val"}, "prod": {"KEY": "pval"}}))
    freeze_path = tmp_path / "freeze.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.env_freeze.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.env_freeze._get_freeze_path", lambda: freeze_path)
    yield store


def test_freeze_add_success(runner):
    result = runner.invoke(cmd_freeze, ["add", "dev"])
    assert result.exit_code == 0
    assert "Frozen 'dev'" in result.output


def test_freeze_add_specific_key(runner):
    result = runner.invoke(cmd_freeze, ["add", "dev", "KEY"])
    assert result.exit_code == 0
    assert "KEY" in result.output


def test_freeze_add_missing_profile_fails(runner):
    result = runner.invoke(cmd_freeze, ["add", "ghost"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_freeze_remove_success(runner):
    runner.invoke(cmd_freeze, ["add", "dev"])
    result = runner.invoke(cmd_freeze, ["remove", "dev"])
    assert result.exit_code == 0
    assert "Unfrozen" in result.output


def test_freeze_remove_not_frozen_fails(runner):
    result = runner.invoke(cmd_freeze, ["remove", "dev"])
    assert result.exit_code != 0


def test_freeze_status_frozen(runner):
    runner.invoke(cmd_freeze, ["add", "dev"])
    result = runner.invoke(cmd_freeze, ["status", "dev"])
    assert "frozen" in result.output
    assert result.exit_code == 0


def test_freeze_status_not_frozen(runner):
    result = runner.invoke(cmd_freeze, ["status", "dev"])
    assert "not frozen" in result.output


def test_freeze_list_empty(runner):
    result = runner.invoke(cmd_freeze, ["list"])
    assert "No frozen" in result.output


def test_freeze_list_shows_profiles(runner):
    runner.invoke(cmd_freeze, ["add", "dev"])
    runner.invoke(cmd_freeze, ["add", "prod"])
    result = runner.invoke(cmd_freeze, ["list"])
    assert "dev" in result.output
    assert "prod" in result.output
