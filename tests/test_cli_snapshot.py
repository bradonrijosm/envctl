"""Integration tests for the snapshot CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envctl.cli_snapshot import cmd_snapshot
from envctl.storage import save_profiles, load_profiles


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "envctl_store.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.snapshot.get_store_path", lambda: store)
    yield store


@pytest.fixture()
def runner():
    return CliRunner()


def _seed(profiles: dict) -> None:
    save_profiles(profiles)


def test_snapshot_create_success(runner):
    _seed({"dev": {"X": "1"}})
    result = runner.invoke(cmd_snapshot, ["create", "my-snap"])
    assert result.exit_code == 0
    assert "my-snap" in result.output
    assert "created" in result.output


def test_snapshot_create_duplicate_fails(runner):
    _seed({"dev": {"X": "1"}})
    runner.invoke(cmd_snapshot, ["create", "dup"])
    result = runner.invoke(cmd_snapshot, ["create", "dup"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_snapshot_restore_with_yes_flag(runner):
    _seed({"dev": {"KEY": "before"}})
    runner.invoke(cmd_snapshot, ["create", "snap"])
    _seed({"dev": {"KEY": "after"}})
    result = runner.invoke(cmd_snapshot, ["restore", "snap", "--yes"])
    assert result.exit_code == 0
    assert load_profiles()["dev"]["KEY"] == "before"


def test_snapshot_restore_missing_fails(runner):
    result = runner.invoke(cmd_snapshot, ["restore", "ghost", "--yes"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_snapshot_delete_success(runner):
    _seed({"dev": {}})
    runner.invoke(cmd_snapshot, ["create", "to-delete"])
    result = runner.invoke(cmd_snapshot, ["delete", "to-delete"])
    assert result.exit_code == 0
    list_result = runner.invoke(cmd_snapshot, ["list"])
    assert "to-delete" not in list_result.output


def test_snapshot_list_empty(runner):
    result = runner.invoke(cmd_snapshot, ["list"])
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_snapshot_list_shows_entries(runner):
    _seed({"dev": {"A": "1"}, "prod": {"A": "2"}})
    runner.invoke(cmd_snapshot, ["create", "snap-a"])
    result = runner.invoke(cmd_snapshot, ["list"])
    assert "snap-a" in result.output
    assert "2 profile(s)" in result.output
