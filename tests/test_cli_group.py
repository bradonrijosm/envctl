"""CLI integration tests for group commands."""
import json
import pytest
from click.testing import CliRunner

from envctl.cli_group import cmd_group


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "store.json"
    store.write_text(json.dumps({"dev": {"KEY": "val"}, "prod": {"KEY": "p"}}))
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.group.get_store_path", lambda: store)
    yield store


@pytest.fixture()
def runner():
    return CliRunner()


def _seed(runner):
    runner.invoke(cmd_group, ["create", "mygroup"])


def test_group_create_success(isolated_store, runner):
    result = runner.invoke(cmd_group, ["create", "mygroup"])
    assert result.exit_code == 0
    assert "created" in result.output


def test_group_create_duplicate_fails(isolated_store, runner):
    runner.invoke(cmd_group, ["create", "mygroup"])
    result = runner.invoke(cmd_group, ["create", "mygroup"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_group_delete_success(isolated_store, runner):
    _seed(runner)
    result = runner.invoke(cmd_group, ["delete", "mygroup"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_group_add_profile_success(isolated_store, runner):
    _seed(runner)
    result = runner.invoke(cmd_group, ["add", "mygroup", "dev"])
    assert result.exit_code == 0
    assert "added" in result.output


def test_group_add_missing_profile_fails(isolated_store, runner):
    _seed(runner)
    result = runner.invoke(cmd_group, ["add", "mygroup", "ghost"])
    assert result.exit_code == 1


def test_group_remove_profile_success(isolated_store, runner):
    _seed(runner)
    runner.invoke(cmd_group, ["add", "mygroup", "dev"])
    result = runner.invoke(cmd_group, ["remove", "mygroup", "dev"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_group_list_empty(isolated_store, runner):
    result = runner.invoke(cmd_group, ["list"])
    assert result.exit_code == 0
    assert "No groups" in result.output


def test_group_list_shows_groups(isolated_store, runner):
    _seed(runner)
    runner.invoke(cmd_group, ["add", "mygroup", "dev"])
    result = runner.invoke(cmd_group, ["list"])
    assert "mygroup" in result.output
    assert "dev" in result.output


def test_group_show_success(isolated_store, runner):
    _seed(runner)
    runner.invoke(cmd_group, ["add", "mygroup", "prod"])
    result = runner.invoke(cmd_group, ["show", "mygroup"])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_group_show_missing_fails(isolated_store, runner):
    result = runner.invoke(cmd_group, ["show", "ghost"])
    assert result.exit_code == 1
