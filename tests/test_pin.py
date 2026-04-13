"""Tests for envctl.pin."""

from __future__ import annotations

import pytest

from envctl.pin import (
    PinError,
    get_pinned,
    list_pins,
    pin_profile,
    unpin_profile,
)
from envctl.storage import save_profiles


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: tmp_path)
    monkeypatch.setattr("envctl.pin.get_store_path", lambda: tmp_path)
    yield tmp_path


def _seed(profiles: dict) -> None:
    save_profiles(profiles)


def test_pin_profile_success():
    _seed({"dev": {"KEY": "val"}})
    pin_profile("myproject", "dev")
    assert get_pinned("myproject") == "dev"


def test_pin_profile_persists(tmp_path):
    _seed({"staging": {"A": "1"}})
    pin_profile("app", "staging")
    pins = list_pins()
    assert pins["app"] == "staging"


def test_pin_nonexistent_profile_raises():
    _seed({})
    with pytest.raises(PinError, match="does not exist"):
        pin_profile("proj", "ghost")


def test_unpin_profile_success():
    _seed({"prod": {"ENV": "production"}})
    pin_profile("service", "prod")
    unpin_profile("service")
    assert get_pinned("service") is None


def test_unpin_missing_project_raises():
    with pytest.raises(PinError, match="No pinned profile"):
        unpin_profile("nonexistent-project")


def test_get_pinned_returns_none_when_not_set():
    assert get_pinned("unknown") is None


def test_list_pins_empty():
    assert list_pins() == {}


def test_list_pins_multiple():
    _seed({"alpha": {}, "beta": {}, "gamma": {}})
    pin_profile("proj-a", "alpha")
    pin_profile("proj-b", "beta")
    pins = list_pins()
    assert pins == {"proj-a": "alpha", "proj-b": "beta"}


def test_pin_overwrites_existing_pin():
    _seed({"dev": {}, "prod": {}})
    pin_profile("myapp", "dev")
    pin_profile("myapp", "prod")
    assert get_pinned("myapp") == "prod"
