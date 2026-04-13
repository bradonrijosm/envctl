"""Tests for the encrypt CLI commands."""

import pytest
from click.testing import CliRunner

from envctl.cli_encrypt import cmd_encrypt
from envctl.storage import set_profile


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store_file = tmp_path / "profiles.json"
    monkeypatch.setenv("ENVCTL_STORE", str(store_file))
    yield tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def _seed(name, variables):
    set_profile(name, variables)


def test_encrypt_store_success(runner):
    _seed("prod", {"KEY": "value"})
    result = runner.invoke(cmd_encrypt, ["store", "prod", "--passphrase", "secret"])
    assert result.exit_code == 0
    assert "encrypted and stored" in result.output


def test_encrypt_store_missing_profile(runner):
    result = runner.invoke(cmd_encrypt, ["store", "ghost", "--passphrase", "secret"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_encrypt_load_bash_output(runner):
    _seed("staging", {"DB_URL": "postgres://localhost"})
    runner.invoke(cmd_encrypt, ["store", "staging", "--passphrase", "pass"])
    result = runner.invoke(cmd_encrypt, ["load", "staging", "--passphrase", "pass", "--format", "bash"])
    assert result.exit_code == 0
    assert "export DB_URL" in result.output


def test_encrypt_load_raw_output(runner):
    _seed("dev", {"TOKEN": "abc"})
    runner.invoke(cmd_encrypt, ["store", "dev", "--passphrase", "pass"])
    result = runner.invoke(cmd_encrypt, ["load", "dev", "--passphrase", "pass", "--format", "raw"])
    assert result.exit_code == 0
    assert "TOKEN=abc" in result.output


def test_encrypt_load_wrong_passphrase(runner):
    _seed("prod", {"X": "1"})
    runner.invoke(cmd_encrypt, ["store", "prod", "--passphrase", "correct"])
    result = runner.invoke(cmd_encrypt, ["load", "prod", "--passphrase", "wrong"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_encrypt_delete_success(runner):
    _seed("tmp", {"A": "1"})
    runner.invoke(cmd_encrypt, ["store", "tmp", "--passphrase", "pass"])
    result = runner.invoke(cmd_encrypt, ["delete", "tmp"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_encrypt_delete_nonexistent(runner):
    result = runner.invoke(cmd_encrypt, ["delete", "nope"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_encrypt_list_empty(runner):
    result = runner.invoke(cmd_encrypt, ["list"])
    assert result.exit_code == 0
    assert "No encrypted profiles" in result.output


def test_encrypt_list_shows_names(runner):
    _seed("alpha", {"A": "1"})
    _seed("beta", {"B": "2"})
    runner.invoke(cmd_encrypt, ["store", "alpha", "--passphrase", "p"])
    runner.invoke(cmd_encrypt, ["store", "beta", "--passphrase", "p"])
    result = runner.invoke(cmd_encrypt, ["list"])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output
