"""Tests for envctl.promote."""

import pytest
from unittest.mock import patch
from envctl.promote import promote_profile, PromoteError


BASE_PROFILES = {
    "staging": {"variables": {"APP_URL": "https://staging.example.com", "DEBUG": "true"}},
    "production": {"variables": {"APP_URL": "https://example.com"}},
    "empty": {"variables": {}},
}


def _profiles():
    import copy
    return copy.deepcopy(BASE_PROFILES)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCTL_STORE", str(tmp_path / "store.json"))
    from envctl import storage
    storage._cache = None  # type: ignore[attr-defined]
    yield


def _seed():
    from envctl.storage import save_profiles
    save_profiles(_profiles())


def test_promote_all_keys_no_overwrite():
    _seed()
    promoted = promote_profile("staging", "production")
    # APP_URL already exists in production; only DEBUG should be promoted
    assert "DEBUG" in promoted
    assert "APP_URL" not in promoted


def test_promote_all_keys_with_overwrite():
    _seed()
    promoted = promote_profile("staging", "production", overwrite=True)
    assert promoted["APP_URL"] == "https://staging.example.com"
    assert promoted["DEBUG"] == "true"


def test_promote_specific_key():
    _seed()
    promoted = promote_profile("staging", "empty", keys=["APP_URL"])
    assert list(promoted.keys()) == ["APP_URL"]
    assert promoted["APP_URL"] == "https://staging.example.com"


def test_promote_persists_to_store():
    _seed()
    promote_profile("staging", "empty")
    from envctl.storage import load_profiles
    profiles = load_profiles()
    assert profiles["empty"]["variables"]["DEBUG"] == "true"


def test_promote_same_source_and_target_raises():
    _seed()
    with pytest.raises(PromoteError, match="must be different"):
        promote_profile("staging", "staging")


def test_promote_missing_source_raises():
    _seed()
    with pytest.raises(PromoteError, match="Source profile 'nope' does not exist"):
        promote_profile("nope", "production")


def test_promote_missing_target_raises():
    _seed()
    with pytest.raises(PromoteError, match="Target profile 'nope' does not exist"):
        promote_profile("staging", "nope")


def test_promote_missing_key_raises():
    _seed()
    with pytest.raises(PromoteError, match="Keys not found in source"):
        promote_profile("staging", "production", keys=["NONEXISTENT"])


def test_promote_returns_empty_when_nothing_to_do():
    _seed()
    # APP_URL already in production and DEBUG not requested
    promoted = promote_profile("staging", "production", keys=["APP_URL"])
    assert promoted == {}
