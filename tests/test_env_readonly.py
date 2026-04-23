"""Tests for envctl.env_readonly."""

from __future__ import annotations

import json
import pytest

from envctl.env_readonly import (
    ReadonlyError,
    mark_readonly,
    unmark_readonly,
    is_readonly,
    assert_writable,
    list_readonly,
    _get_readonly_path,
)


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    store_file = tmp_path / "profiles.json"
    store_file.write_text(json.dumps({}))
    monkeypatch.setattr("envctl.env_readonly.get_store_path", lambda: store_file)
    monkeypatch.setattr(
        "envctl.env_readonly.get_profile",
        lambda name: {"KEY": "val"} if name in ("dev", "prod", "staging") else None,
    )
    yield tmp_path


def _seed(isolated_store, *names):
    for name in names:
        mark_readonly(name)


def test_mark_readonly_success(isolated_store):
    mark_readonly("dev")
    assert is_readonly("dev")


def test_mark_readonly_persists(isolated_store):
    mark_readonly("dev")
    path = _get_readonly_path()
    data = json.loads(path.read_text())
    assert "dev" in data


def test_mark_readonly_missing_profile_raises(isolated_store):
    with pytest.raises(ReadonlyError, match="does not exist"):
        mark_readonly("ghost")


def test_mark_readonly_duplicate_raises(isolated_store):
    mark_readonly("dev")
    with pytest.raises(ReadonlyError, match="already read-only"):
        mark_readonly("dev")


def test_unmark_readonly_success(isolated_store):
    _seed(isolated_store, "dev")
    unmark_readonly("dev")
    assert not is_readonly("dev")


def test_unmark_readonly_not_marked_raises(isolated_store):
    with pytest.raises(ReadonlyError, match="not marked read-only"):
        unmark_readonly("dev")


def test_is_readonly_false_when_absent(isolated_store):
    assert not is_readonly("dev")


def test_is_readonly_true_when_marked(isolated_store):
    _seed(isolated_store, "prod")
    assert is_readonly("prod")


def test_assert_writable_raises_for_readonly(isolated_store):
    _seed(isolated_store, "prod")
    with pytest.raises(ReadonlyError, match="read-only"):
        assert_writable("prod")


def test_assert_writable_passes_for_normal(isolated_store):
    assert_writable("dev")  # should not raise


def test_list_readonly_empty(isolated_store):
    assert list_readonly() == []


def test_list_readonly_sorted(isolated_store):
    _seed(isolated_store, "staging", "dev", "prod")
    assert list_readonly() == ["dev", "prod", "staging"]
