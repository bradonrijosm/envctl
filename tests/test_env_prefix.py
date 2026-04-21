"""Tests for envctl.env_prefix (add_prefix / strip_prefix)."""

import json
import os
import pytest

from envctl import storage
from envctl.env_prefix import PrefixError, add_prefix, strip_prefix


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr(storage, "get_store_path", lambda: str(store))
    yield store


def _seed(vars_: dict, name: str = "dev"):
    from envctl.storage import set_profile
    set_profile(name, {"variables": vars_})


# ---------------------------------------------------------------------------
# add_prefix
# ---------------------------------------------------------------------------

def test_add_prefix_prepends_to_all_keys():
    _seed({"HOST": "localhost", "PORT": "5432"})
    result = add_prefix("dev", "APP_")
    assert "APP_HOST" in result
    assert "APP_PORT" in result
    assert result["APP_HOST"] == "localhost"


def test_add_prefix_persists_to_store():
    _seed({"KEY": "val"})
    add_prefix("dev", "X_")
    from envctl.storage import get_profile
    stored = get_profile("dev")
    assert "X_KEY" in stored["variables"]
    assert "KEY" not in stored["variables"]


def test_add_prefix_empty_prefix_raises():
    _seed({"A": "1"})
    with pytest.raises(PrefixError, match="non-empty"):
        add_prefix("dev", "")


def test_add_prefix_missing_profile_raises():
    with pytest.raises(PrefixError, match="not found"):
        add_prefix("ghost", "P_")


def test_add_prefix_collision_raises_by_default():
    # APP_HOST already exists; adding APP_ to HOST would produce APP_HOST again
    _seed({"HOST": "a", "APP_HOST": "b"})
    with pytest.raises(PrefixError, match="already exists"):
        add_prefix("dev", "APP_")


def test_add_prefix_collision_allowed_with_overwrite():
    _seed({"HOST": "new", "APP_HOST": "old"})
    result = add_prefix("dev", "APP_", overwrite=True)
    assert result["APP_HOST"] == "new"


# ---------------------------------------------------------------------------
# strip_prefix
# ---------------------------------------------------------------------------

def test_strip_prefix_removes_prefix_from_all_keys():
    _seed({"APP_HOST": "localhost", "APP_PORT": "5432"})
    result = strip_prefix("dev", "APP_")
    assert "HOST" in result
    assert "PORT" in result
    assert "APP_HOST" not in result


def test_strip_prefix_persists_to_store():
    _seed({"CI_TOKEN": "abc"})
    strip_prefix("dev", "CI_")
    from envctl.storage import get_profile
    stored = get_profile("dev")
    assert "TOKEN" in stored["variables"]


def test_strip_prefix_missing_key_raises_by_default():
    _seed({"APP_HOST": "h", "OTHER": "x"})
    with pytest.raises(PrefixError, match="does not start with prefix"):
        strip_prefix("dev", "APP_")


def test_strip_prefix_ignore_missing_keeps_unmatched_keys():
    _seed({"APP_HOST": "h", "OTHER": "x"})
    result = strip_prefix("dev", "APP_", ignore_missing=True)
    assert "HOST" in result
    assert "OTHER" in result


def test_strip_prefix_empty_prefix_raises():
    _seed({"A": "1"})
    with pytest.raises(PrefixError, match="non-empty"):
        strip_prefix("dev", "")


def test_strip_prefix_missing_profile_raises():
    with pytest.raises(PrefixError, match="not found"):
        strip_prefix("ghost", "X_")
