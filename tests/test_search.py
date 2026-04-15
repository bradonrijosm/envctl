"""Tests for envctl.search module."""

from __future__ import annotations

import pytest

from envctl.search import SearchError, search_by_key, search_by_value, search_profiles
from envctl.storage import save_profiles


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.search.load_profiles", lambda: _load())

    def _load():
        from envctl.storage import load_profiles as _lp
        return _lp()

    save_profiles({
        "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET_KEY": "dev-secret"},
        "prod": {"DB_HOST": "prod.db.example.com", "DB_PORT": "5432", "SECRET_KEY": "prod-secret"},
        "staging": {"API_URL": "https://staging.api.example.com", "DEBUG": "false"},
    })
    monkeypatch.undo()
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.search.load_profiles", lambda: _load())


def test_search_by_key_exact_glob():
    results = search_by_key("DB_HOST")
    assert len(results) == 2
    assert all(m.key == "DB_HOST" for m in results)


def test_search_by_key_wildcard():
    results = search_by_key("DB_*")
    assert len(results) == 4  # DB_HOST x2, DB_PORT x2
    keys = {m.key for m in results}
    assert keys == {"DB_HOST", "DB_PORT"}


def test_search_by_key_case_insensitive_default():
    results = search_by_key("db_host")
    assert len(results) == 2


def test_search_by_key_case_sensitive_no_match():
    results = search_by_key("db_host", case_sensitive=True)
    assert results == []


def test_search_by_value_glob():
    results = search_by_value("*secret*")
    assert len(results) == 2
    assert all("secret" in m.value for m in results)


def test_search_by_value_exact():
    results = search_by_value("5432")
    assert len(results) == 2
    assert all(m.key == "DB_PORT" for m in results)


def test_search_profiles_key_and_value():
    results = search_profiles(key_pattern="DB_HOST", value_pattern="localhost")
    assert len(results) == 1
    assert results[0].profile == "dev"
    assert results[0].key == "DB_HOST"


def test_search_profiles_no_pattern_raises():
    with pytest.raises(SearchError):
        search_profiles()


def test_search_profiles_key_only():
    results = search_profiles(key_pattern="SECRET_KEY")
    assert len(results) == 2
    profiles = {m.profile for m in results}
    assert profiles == {"dev", "prod"}


def test_search_profiles_no_results():
    results = search_profiles(key_pattern="NONEXISTENT_VAR")
    assert results == []
