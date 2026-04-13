"""Tests for envctl.diff module."""

import pytest
from envctl.diff import diff_profiles, format_diff, DiffEntry


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
TARGET = {"HOST": "prod.example.com", "PORT": "5432", "LOG_LEVEL": "warn"}


def test_diff_detects_added_keys():
    entries = diff_profiles(BASE, TARGET)
    added = [e for e in entries if e.status == "added"]
    assert len(added) == 1
    assert added[0].key == "LOG_LEVEL"
    assert added[0].new_value == "warn"


def test_diff_detects_removed_keys():
    entries = diff_profiles(BASE, TARGET)
    removed = [e for e in entries if e.status == "removed"]
    assert len(removed) == 1
    assert removed[0].key == "DEBUG"
    assert removed[0].old_value == "true"


def test_diff_detects_changed_keys():
    entries = diff_profiles(BASE, TARGET)
    changed = [e for e in entries if e.status == "changed"]
    assert len(changed) == 1
    assert changed[0].key == "HOST"
    assert changed[0].old_value == "localhost"
    assert changed[0].new_value == "prod.example.com"


def test_diff_unchanged_excluded_by_default():
    entries = diff_profiles(BASE, TARGET)
    unchanged = [e for e in entries if e.status == "unchanged"]
    assert unchanged == []


def test_diff_unchanged_included_when_requested():
    entries = diff_profiles(BASE, TARGET, show_unchanged=True)
    unchanged = [e for e in entries if e.status == "unchanged"]
    assert len(unchanged) == 1
    assert unchanged[0].key == "PORT"


def test_diff_identical_profiles_returns_empty():
    entries = diff_profiles(BASE, BASE)
    assert entries == []


def test_format_diff_no_differences():
    result = format_diff([])
    assert result == "(no differences)"


def test_format_diff_contains_key_info():
    entries = diff_profiles(BASE, TARGET)
    output = format_diff(entries, color=False)
    assert "HOST" in output
    assert "DEBUG" in output
    assert "LOG_LEVEL" in output


def test_format_diff_symbols_no_color():
    entries = diff_profiles(BASE, TARGET)
    output = format_diff(entries, color=False)
    lines = output.splitlines()
    statuses = {e.key: e.status for e in entries}
    for line in lines:
        sym = line[0]
        key = line[2:].split("=")[0].split(":")[0]
        if statuses.get(key) == "added":
            assert sym == "+"
        elif statuses.get(key) == "removed":
            assert sym == "-"
        elif statuses.get(key) == "changed":
            assert sym == "~"


def test_format_diff_color_escape_codes():
    entries = [DiffEntry(key="FOO", status="added", new_value="bar")]
    output = format_diff(entries, color=True)
    assert "\033[" in output
