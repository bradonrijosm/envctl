"""Tests for envctl.env_freeze."""

from __future__ import annotations

import json
import pytest

from envctl.env_freeze import (
    FreezeError,
    freeze_profile,
    unfreeze_profile,
    is_frozen,
    list_frozen,
    assert_not_frozen,
    _get_freeze_path,
)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    store.write_text(json.dumps({"dev": {"KEY": "val", "SECRET": "s"}}))
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.env_freeze.get_store_path", lambda: store)
    yield store


def _seed_freeze(tmp_path, data: dict) -> None:
    freeze_path = tmp_path / "freeze.json"
    freeze_path.write_text(json.dumps(data))


def test_freeze_profile_all_keys(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.env_freeze._get_freeze_path", lambda: tmp_path / "freeze.json")
    freeze_profile("dev")
    assert is_frozen("dev")


def test_freeze_profile_specific_keys(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.env_freeze._get_freeze_path", lambda: tmp_path / "freeze.json")
    freeze_profile("dev", ["SECRET"])
    assert is_frozen("dev", "SECRET")
    assert not is_frozen("dev", "KEY")


def test_freeze_nonexistent_profile_raises(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.env_freeze._get_freeze_path", lambda: tmp_path / "freeze.json")
    with pytest.raises(FreezeError, match="does not exist"):
        freeze_profile("ghost")


def test_freeze_already_fully_frozen_raises(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.env_freeze._get_freeze_path", lambda: tmp_path / "freeze.json")
    freeze_profile("dev")
    with pytest.raises(FreezeError, match="already fully frozen"):
        freeze_profile("dev", ["KEY"])


def test_unfreeze_profile_all(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.env_freeze._get_freeze_path", lambda: tmp_path / "freeze.json")
    freeze_profile("dev")
    unfreeze_profile("dev")
    assert not is_frozen("dev")


def test_unfreeze_specific_keys(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.env_freeze._get_freeze_path", lambda: tmp_path / "freeze.json")
    freeze_profile("dev", ["KEY", "SECRET"])
    unfreeze_profile("dev", ["SECRET"])
    assert is_frozen("dev", "KEY")
    assert not is_frozen("dev", "SECRET")


def test_unfreeze_not_frozen_raises(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.env_freeze._get_freeze_path", lambda: tmp_path / "freeze.json")
    with pytest.raises(FreezeError, match="not frozen"):
        unfreeze_profile("dev")


def test_unfreeze_partial_on_full_freeze_raises(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.env_freeze._get_freeze_path", lambda: tmp_path / "freeze.json")
    freeze_profile("dev")
    with pytest.raises(FreezeError, match="fully frozen"):
        unfreeze_profile("dev", ["KEY"])


def test_list_frozen_returns_all(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.env_freeze._get_freeze_path", lambda: tmp_path / "freeze.json")
    freeze_profile("dev")
    result = list_frozen()
    assert "dev" in result


def test_assert_not_frozen_raises_when_frozen(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.env_freeze._get_freeze_path", lambda: tmp_path / "freeze.json")
    freeze_profile("dev")
    with pytest.raises(FreezeError, match="frozen"):
        assert_not_frozen("dev")


def test_assert_not_frozen_passes_when_unfrozen(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.env_freeze._get_freeze_path", lambda: tmp_path / "freeze.json")
    assert_not_frozen("dev")  # should not raise
