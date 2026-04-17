"""Tests for envctl.ttl module."""
import time
import pytest

from envctl.ttl import (
    TTLError, set_ttl, get_ttl, remove_ttl, is_expired, list_ttls,
    _get_ttl_path,
)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    store.write_text('{"dev": {"API_KEY": "abc"}}')
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.ttl.get_store_path", lambda: store)
    yield tmp_path


def test_set_ttl_success():
    set_ttl("dev", 60)
    expires = get_ttl("dev")
    assert expires is not None
    assert expires > time.time()


def test_set_ttl_missing_profile_raises():
    with pytest.raises(TTLError, match="does not exist"):
        set_ttl("ghost", 60)


def test_set_ttl_zero_seconds_raises():
    with pytest.raises(TTLError, match="positive"):
        set_ttl("dev", 0)


def test_get_ttl_no_entry_returns_none():
    assert get_ttl("dev") is None


def test_remove_ttl_success():
    set_ttl("dev", 60)
    remove_ttl("dev")
    assert get_ttl("dev") is None


def test_remove_ttl_missing_raises():
    with pytest.raises(TTLError, match="No TTL set"):
        remove_ttl("dev")


def test_is_expired_not_expired():
    set_ttl("dev", 3600)
    assert is_expired("dev") is False


def test_is_expired_no_ttl_returns_false():
    assert is_expired("dev") is False


def test_is_expired_past_expiry(monkeypatch):
    set_ttl("dev", 1)
    monkeypatch.setattr("envctl.ttl.time", type("T", (), {"time": staticmethod(lambda: time.time() + 10)})())
    assert is_expired("dev") is True


def test_list_ttls_empty():
    assert list_ttls() == []


def test_list_ttls_shows_entry():
    set_ttl("dev", 120)
    entries = list_ttls()
    assert len(entries) == 1
    assert entries[0]["profile"] == "dev"
    assert entries[0]["expired"] is False
    assert entries[0]["remaining_seconds"] > 0
