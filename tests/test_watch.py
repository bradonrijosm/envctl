"""Tests for envctl.watch."""

from __future__ import annotations

import pytest
from unittest.mock import patch, call

from envctl.watch import WatchError, _hash_profile, watch_profile


# ---------------------------------------------------------------------------
# _hash_profile
# ---------------------------------------------------------------------------

def test_hash_profile_stable():
    vars1 = {"A": "1", "B": "2"}
    assert _hash_profile(vars1) == _hash_profile(vars1)


def test_hash_profile_order_independent():
    assert _hash_profile({"A": "1", "B": "2"}) == _hash_profile({"B": "2", "A": "1"})


def test_hash_profile_differs_on_change():
    assert _hash_profile({"A": "1"}) != _hash_profile({"A": "2"})


# ---------------------------------------------------------------------------
# watch_profile
# ---------------------------------------------------------------------------

def test_watch_profile_missing_raises():
    with patch("envctl.watch._current_variables", return_value=None):
        with pytest.raises(WatchError, match="does not exist"):
            watch_profile("ghost", lambda *a: None, interval=0, max_iterations=0)


def test_watch_profile_no_change_no_callback():
    initial = {"X": "1"}
    calls = []

    with patch("envctl.watch._current_variables", side_effect=[initial, initial]):
        with patch("envctl.watch.time.sleep"):
            watch_profile("p", lambda *a: calls.append(a), interval=0, max_iterations=1)

    assert calls == []


def test_watch_profile_change_triggers_callback():
    initial = {"X": "1"}
    updated = {"X": "2"}
    calls = []

    with patch("envctl.watch._current_variables", side_effect=[initial, updated]):
        with patch("envctl.watch.time.sleep"):
            watch_profile("p", lambda *a: calls.append(a), interval=0, max_iterations=1)

    assert len(calls) == 1
    name, old, new = calls[0]
    assert name == "p"
    assert old == initial
    assert new == updated


def test_watch_profile_removed_during_watch_raises():
    initial = {"X": "1"}

    with patch("envctl.watch._current_variables", side_effect=[initial, None]):
        with patch("envctl.watch.time.sleep"):
            with pytest.raises(WatchError, match="removed during watch"):
                watch_profile("p", lambda *a: None, interval=0, max_iterations=1)


def test_watch_profile_multiple_changes():
    snapshots = [{"X": "1"}, {"X": "2"}, {"X": "3"}]
    calls = []

    with patch("envctl.watch._current_variables", side_effect=snapshots):
        with patch("envctl.watch.time.sleep"):
            watch_profile("p", lambda *a: calls.append(a), interval=0, max_iterations=2)

    assert len(calls) == 2
