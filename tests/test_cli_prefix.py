"""CLI integration tests for the `envctl prefix` command group."""

import pytest
from click.testing import CliRunner

from envctl import storage
from envctl.cli_prefix import cmd_prefix


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr(storage, "get_store_path", lambda: str(store))
    yield store


@pytest.fixture()
def runner():
    return CliRunner()


def _seed(vars_: dict, name: str = "dev"):
    from envctl.storage import set_profile
    set_profile(name, {"variables": vars_})


# ---------------------------------------------------------------------------
# prefix add
# ---------------------------------------------------------------------------

def test_prefix_add_success(runner):
    _seed({"HOST": "localhost", "PORT": "3000"})
    result = runner.invoke(cmd_prefix, ["add", "dev", "APP_"])
    assert result.exit_code == 0
    assert "APP_" in result.output
    assert "2" in result.output  # 2 keys updated


def test_prefix_add_missing_profile_fails(runner):
    result = runner.invoke(cmd_prefix, ["add", "ghost", "X_"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_prefix_add_collision_fails_without_flag(runner):
    _seed({"HOST": "a", "APP_HOST": "b"})
    result = runner.invoke(cmd_prefix, ["add", "dev", "APP_"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_prefix_add_collision_ok_with_overwrite_flag(runner):
    _seed({"HOST": "new", "APP_HOST": "old"})
    result = runner.invoke(cmd_prefix, ["add", "dev", "APP_", "--overwrite"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# prefix strip
# ---------------------------------------------------------------------------

def test_prefix_strip_success(runner):
    _seed({"APP_HOST": "h", "APP_PORT": "p"})
    result = runner.invoke(cmd_prefix, ["strip", "dev", "APP_"])
    assert result.exit_code == 0
    assert "2" in result.output


def test_prefix_strip_missing_profile_fails(runner):
    result = runner.invoke(cmd_prefix, ["strip", "ghost", "X_"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_prefix_strip_unmatched_key_fails_by_default(runner):
    _seed({"APP_HOST": "h", "OTHER": "x"})
    result = runner.invoke(cmd_prefix, ["strip", "dev", "APP_"])
    assert result.exit_code != 0
    assert "does not start with prefix" in result.output


def test_prefix_strip_ignore_missing_flag(runner):
    _seed({"APP_HOST": "h", "OTHER": "x"})
    result = runner.invoke(cmd_prefix, ["strip", "dev", "APP_", "--ignore-missing"])
    assert result.exit_code == 0
