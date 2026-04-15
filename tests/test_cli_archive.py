"""CLI tests for envctl.cli_archive."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from envctl.cli_archive import cmd_archive


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "store.json"
    store.write_text(json.dumps({"dev": {"API_KEY": "abc"}}))
    monkeypatch.setattr("envctl.archive.load_profiles",
                        lambda: json.loads(store.read_text()))
    monkeypatch.setattr("envctl.archive.save_profiles",
                        lambda d: store.write_text(json.dumps(d)))
    return tmp_path


def test_archive_create_success(runner, isolated_store):
    dest = str(isolated_store / "out.zip")
    result = runner.invoke(cmd_archive, ["create", dest, "--label", "ci"])
    assert result.exit_code == 0
    assert "Archive created" in result.output


def test_archive_create_no_label(runner, isolated_store):
    dest = str(isolated_store / "out.zip")
    result = runner.invoke(cmd_archive, ["create", dest])
    assert result.exit_code == 0


def test_archive_inspect_success(runner, isolated_store):
    dest = isolated_store / "snap.zip"
    with zipfile.ZipFile(dest, "w") as zf:
        zf.writestr("profiles.json", json.dumps({"staging": {}}))
        zf.writestr("envctl_manifest.json",
                    json.dumps({"label": "snap1", "created_at": "2024-01-01T00:00:00+00:00", "profile_count": 1}))
    result = runner.invoke(cmd_archive, ["inspect", str(dest)])
    assert result.exit_code == 0
    assert "snap1" in result.output
    assert "staging" in result.output


def test_archive_inspect_missing_fails(runner, isolated_store):
    result = runner.invoke(cmd_archive, ["inspect", str(isolated_store / "ghost.zip")])
    assert result.exit_code != 0


def test_archive_restore_success(runner, isolated_store):
    dest = isolated_store / "snap.zip"
    with zipfile.ZipFile(dest, "w") as zf:
        zf.writestr("profiles.json", json.dumps({"prod": {"X": "1"}}))
        zf.writestr("envctl_manifest.json",
                    json.dumps({"label": "prod-snap", "created_at": "2024-01-01T00:00:00+00:00"}))
    result = runner.invoke(cmd_archive, ["restore", str(dest)])
    assert result.exit_code == 0
    assert "prod-snap" in result.output


def test_archive_restore_missing_fails(runner, isolated_store):
    result = runner.invoke(cmd_archive, ["restore", str(isolated_store / "no.zip")])
    assert result.exit_code != 0
