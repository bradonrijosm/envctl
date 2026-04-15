"""CLI tests for the compare command group."""

import json
import pytest
from click.testing import CliRunner

from envctl.cli_compare import cmd_compare
from envctl.storage import save_profiles


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    return store


@pytest.fixture()
def runner():
    return CliRunner()


def _seed(profiles):
    save_profiles(profiles)


def test_compare_show_identical(runner, isolated_store):
    _seed({"dev": {"X": "1"}, "staging": {"X": "1"}})
    result = runner.invoke(cmd_compare, ["show", "dev", "staging"])
    assert result.exit_code == 0
    assert "identical" in result.output


def test_compare_show_differences(runner, isolated_store):
    _seed({"dev": {"X": "1", "Y": "old"}, "staging": {"X": "1", "Y": "new", "Z": "3"}})
    result = runner.invoke(cmd_compare, ["show", "dev", "staging"])
    assert result.exit_code == 0
    assert "changed" in result.output
    assert "only in staging" in result.output


def test_compare_show_json_output(runner, isolated_store):
    _seed({"dev": {"A": "1"}, "prod": {"A": "2"}})
    result = runner.invoke(cmd_compare, ["show", "dev", "prod", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["identical"] is False
    assert "A" in data["in_both_different"]


def test_compare_show_missing_profile(runner, isolated_store):
    _seed({"dev": {"X": "1"}})
    result = runner.invoke(cmd_compare, ["show", "dev", "ghost"])
    assert result.exit_code != 0
    assert "ghost" in result.output


def test_compare_summary_output(runner, isolated_store):
    _seed({"a": {"K": "v", "M": "1"}, "b": {"K": "v", "M": "2"}})
    result = runner.invoke(cmd_compare, ["summary", "a", "b"])
    assert result.exit_code == 0
    assert "similar" in result.output
    assert "same=1" in result.output
    assert "changed=1" in result.output


def test_compare_summary_missing_profile(runner, isolated_store):
    _seed({"a": {"K": "v"}})
    result = runner.invoke(cmd_compare, ["summary", "a", "missing"])
    assert result.exit_code != 0
