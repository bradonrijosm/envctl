"""Tests for envctl.env_mask."""

from __future__ import annotations

import pytest

from envctl.env_mask import MaskError, _is_sensitive, mask_value, mask_profile


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------

def test_is_sensitive_matches_password():
    assert _is_sensitive("DB_PASSWORD", ["password"]) is True


def test_is_sensitive_case_insensitive():
    assert _is_sensitive("Api_Key", ["api_key"]) is True


def test_is_sensitive_no_match():
    assert _is_sensitive("HOST", ["password", "token"]) is False


def test_mask_value_hides_most_chars():
    result = mask_value("supersecret", reveal_chars=4)
    assert result.endswith("cret")
    assert result.startswith("*")
    assert len(result) == len("supersecret")


def test_mask_value_short_string():
    result = mask_value("abc", reveal_chars=4)
    assert result == "***"


def test_mask_value_exact_reveal_length():
    result = mask_value("1234", reveal_chars=4)
    assert result == "****"


# ---------------------------------------------------------------------------
# Integration tests for mask_profile
# ---------------------------------------------------------------------------

@pytest.fixture()
def _mock_get(monkeypatch):
    """Patch storage.get_profile to return a fixed dict."""
    def _factory(data):
        monkeypatch.setattr("envctl.env_mask.get_profile", lambda name: data.get(name))
    return _factory


def test_mask_profile_sensitive_keys_are_masked(_mock_get):
    _mock_get({"prod": {"DB_PASSWORD": "s3cr3tpass", "HOST": "localhost"}})
    result = mask_profile("prod")
    assert result["HOST"] == "localhost"
    assert "pass" in result["DB_PASSWORD"]
    assert result["DB_PASSWORD"] != "s3cr3tpass"


def test_mask_profile_non_sensitive_unchanged(_mock_get):
    _mock_get({"dev": {"PORT": "8080", "DEBUG": "true"}})
    result = mask_profile("dev")
    assert result == {"PORT": "8080", "DEBUG": "true"}


def test_mask_profile_missing_raises(_mock_get):
    _mock_get({})
    with pytest.raises(MaskError, match="not found"):
        mask_profile("ghost")


def test_mask_profile_custom_patterns(_mock_get):
    _mock_get({"cfg": {"MY_CUSTOM_SENSITIVE": "hidden_val", "NORMAL": "visible"}})
    result = mask_profile("cfg", patterns=["custom_sensitive"])
    assert result["NORMAL"] == "visible"
    assert result["MY_CUSTOM_SENSITIVE"] != "hidden_val"


def test_mask_profile_reveal_chars_respected(_mock_get):
    _mock_get({"x": {"API_TOKEN": "abcdefgh"}})
    result = mask_profile("x", reveal_chars=2)
    assert result["API_TOKEN"].endswith("gh")
    assert result["API_TOKEN"].count("*") == 6
