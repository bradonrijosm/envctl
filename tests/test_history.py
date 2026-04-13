"""Tests for envctl.history."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import envctl.storage as storage
import envctl.history as history
from envctl.history import (
    record_activation,
    get_history,
    clear_history,
    last_activated,
    HistoryError,
    MAX_HISTORY,
)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store_file = tmp_path / "profiles.json"
    monkeypatch.setattr(storage, "get_store_path", lambda: store_file)
    # Patch history path to use the same tmp_path
    monkeypatch.setattr(history, "_get_history_path", lambda: tmp_path / "history.json")
    yield tmp_path


def test_get_history_empty():
    assert get_history() == []


def test_record_activation_creates_entry():
    record_activation("dev")
    entries = get_history()
    assert len(entries) == 1
    assert entries[0]["profile"] == "dev"
    assert "activated_at" in entries[0]


def test_get_history_newest_first():
    for name in ["dev", "staging", "prod"]:
        record_activation(name)
    entries = get_history()
    assert [e["profile"] for e in entries] == ["prod", "staging", "dev"]


def test_get_history_with_limit():
    for name in ["a", "b", "c", "d"]:
        record_activation(name)
    entries = get_history(limit=2)
    assert len(entries) == 2
    assert entries[0]["profile"] == "d"


def test_last_activated_none_when_empty():
    assert last_activated() is None


def test_last_activated_returns_most_recent():
    record_activation("alpha")
    record_activation("beta")
    assert last_activated() == "beta"


def test_clear_history():
    record_activation("dev")
    record_activation("prod")
    clear_history()
    assert get_history() == []
    assert last_activated() is None


def test_history_capped_at_max(isolated_store):
    for i in range(MAX_HISTORY + 10):
        record_activation(f"profile_{i}")
    raw = json.loads((isolated_store / "history.json").read_text())
    assert len(raw) == MAX_HISTORY
    # Oldest entries should have been dropped
    assert raw[0]["profile"] == "profile_10"


def test_history_error_on_corrupt_file(isolated_store):
    hist_path = isolated_store / "history.json"
    hist_path.write_text("{not valid json")
    with pytest.raises(HistoryError):
        get_history()
