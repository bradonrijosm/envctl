"""Tests for envctl.env_reorder."""

from __future__ import annotations

import json
import pathlib
import pytest

from envctl import storage
from envctl.env_reorder import ReorderError, move_key, reorder_keys


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr(storage, "get_store_path", lambda: store)
    return store


def _seed(isolated_store, profiles: dict):
    isolated_store.write_text(json.dumps(profiles))


# ---------------------------------------------------------------------------
# reorder_keys
# ---------------------------------------------------------------------------

def test_reorder_keys_explicit_order(isolated_store):
    _seed(isolated_store, {"dev": {"C": "3", "A": "1", "B": "2"}})
    result = reorder_keys("dev", ["A", "B", "C"])
    assert list(result.keys()) == ["A", "B", "C"]


def test_reorder_keys_partial_order_fills_remaining(isolated_store):
    _seed(isolated_store, {"dev": {"C": "3", "A": "1", "B": "2"}})
    result = reorder_keys("dev", ["B"], fill_remaining=True)
    assert list(result.keys())[0] == "B"
    assert set(result.keys()) == {"A", "B", "C"}


def test_reorder_keys_partial_order_drops_remaining(isolated_store):
    _seed(isolated_store, {"dev": {"C": "3", "A": "1", "B": "2"}})
    result = reorder_keys("dev", ["A", "C"], fill_remaining=False)
    assert list(result.keys()) == ["A", "C"]
    assert "B" not in result


def test_reorder_keys_persists_to_store(isolated_store):
    _seed(isolated_store, {"dev": {"Z": "26", "A": "1"}})
    reorder_keys("dev", ["A", "Z"])
    data = json.loads(isolated_store.read_text())
    assert list(data["dev"].keys()) == ["A", "Z"]


def test_reorder_keys_missing_profile_raises(isolated_store):
    _seed(isolated_store, {})
    with pytest.raises(ReorderError, match="does not exist"):
        reorder_keys("ghost", ["X"])


def test_reorder_keys_unknown_key_raises(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    with pytest.raises(ReorderError, match="Keys not found"):
        reorder_keys("dev", ["A", "MISSING"])


# ---------------------------------------------------------------------------
# move_key
# ---------------------------------------------------------------------------

def test_move_key_to_front(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1", "B": "2", "C": "3"}})
    result = move_key("dev", "C", 0)
    assert list(result.keys()) == ["C", "A", "B"]


def test_move_key_to_end(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1", "B": "2", "C": "3"}})
    result = move_key("dev", "A", 10)  # clamped to end
    assert list(result.keys()) == ["B", "C", "A"]


def test_move_key_middle(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1", "B": "2", "C": "3"}})
    result = move_key("dev", "C", 1)
    assert list(result.keys()) == ["A", "C", "B"]


def test_move_key_persists(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1", "B": "2"}})
    move_key("dev", "B", 0)
    data = json.loads(isolated_store.read_text())
    assert list(data["dev"].keys()) == ["B", "A"]


def test_move_key_missing_profile_raises(isolated_store):
    _seed(isolated_store, {})
    with pytest.raises(ReorderError, match="does not exist"):
        move_key("ghost", "X", 0)


def test_move_key_missing_key_raises(isolated_store):
    _seed(isolated_store, {"dev": {"A": "1"}})
    with pytest.raises(ReorderError, match="not found"):
        move_key("dev", "Z", 0)
