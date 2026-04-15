"""Tests for envctl.rename and envctl.cli_rename."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envctl.cli_rename import cmd_rename
from envctl.rename import RenameError, clone_profile, rename_profile
from envctl.storage import load_profiles, save_profiles


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    return store


def _seed(data: dict) -> None:
    save_profiles(data)


# ---------------------------------------------------------------------------
# rename_profile
# ---------------------------------------------------------------------------

def test_rename_profile_success():
    _seed({"dev": {"A": "1"}, "prod": {"B": "2"}})
    rename_profile("dev", "staging")
    profiles = load_profiles()
    assert "staging" in profiles
    assert profiles["staging"] == {"A": "1"}
    assert "dev" not in profiles


def test_rename_profile_missing_raises():
    _seed({})
    with pytest.raises(RenameError, match="does not exist"):
        rename_profile("ghost", "new")


def test_rename_profile_dest_exists_raises():
    _seed({"dev": {"A": "1"}, "prod": {"B": "2"}})
    with pytest.raises(RenameError, match="already exists"):
        rename_profile("dev", "prod")


# ---------------------------------------------------------------------------
# clone_profile
# ---------------------------------------------------------------------------

def test_clone_profile_full_copy():
    _seed({"dev": {"A": "1", "B": "2"}})
    vars_ = clone_profile("dev", "dev-copy")
    assert vars_ == {"A": "1", "B": "2"}
    profiles = load_profiles()
    assert "dev" in profiles  # original untouched
    assert profiles["dev-copy"] == {"A": "1", "B": "2"}


def test_clone_profile_include_keys():
    _seed({"dev": {"A": "1", "B": "2", "C": "3"}})
    vars_ = clone_profile("dev", "partial", include_keys=["A", "C"])
    assert vars_ == {"A": "1", "C": "3"}


def test_clone_profile_exclude_keys():
    _seed({"dev": {"A": "1", "SECRET": "s3cr3t"}})
    vars_ = clone_profile("dev", "safe", exclude_keys=["SECRET"])
    assert vars_ == {"A": "1"}
    assert "SECRET" not in vars_


def test_clone_profile_missing_source_raises():
    _seed({})
    with pytest.raises(RenameError, match="does not exist"):
        clone_profile("ghost", "new")


def test_clone_profile_dest_exists_raises():
    _seed({"dev": {"A": "1"}, "prod": {"B": "2"}})
    with pytest.raises(RenameError, match="already exists"):
        clone_profile("dev", "prod")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_mv_success(runner):
    _seed({"dev": {"X": "1"}})
    result = runner.invoke(cmd_rename, ["mv", "dev", "staging"])
    assert result.exit_code == 0
    assert "staging" in result.output


def test_cli_mv_missing_profile(runner):
    _seed({})
    result = runner.invoke(cmd_rename, ["mv", "ghost", "new"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_cli_clone_success(runner):
    _seed({"dev": {"A": "1", "B": "2"}})
    result = runner.invoke(cmd_rename, ["clone", "dev", "dev-clone"])
    assert result.exit_code == 0
    assert "2 variable(s)" in result.output


def test_cli_clone_with_exclude(runner):
    _seed({"dev": {"A": "1", "SECRET": "s"}})
    result = runner.invoke(
        cmd_rename, ["clone", "dev", "safe", "--exclude", "SECRET"]
    )
    assert result.exit_code == 0
    assert "1 variable(s)" in result.output
