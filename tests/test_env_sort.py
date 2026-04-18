"""Tests for envctl.env_sort."""
import pytest
from unittest.mock import patch
from envctl.env_sort import sort_profile, SortError

_PROFILE_DATA = {
    "variables": {
        "ZEBRA": "last",
        "ALPHA": "first",
        "MANGO": "middle",
    }
}


def _mock_get(name):
    return _PROFILE_DATA if name == "dev" else None


def _mock_set(name, data):
    pass


def test_sort_by_key_ascending():
    with patch("envctl.env_sort.get_profile", side_effect=_mock_get), \
         patch("envctl.env_sort.set_profile", side_effect=_mock_set):
        result = sort_profile("dev", by="key")
    assert list(result.keys()) == ["ALPHA", "MANGO", "ZEBRA"]


def test_sort_by_key_descending():
    with patch("envctl.env_sort.get_profile", side_effect=_mock_get), \
         patch("envctl.env_sort.set_profile", side_effect=_mock_set):
        result = sort_profile("dev", by="key", reverse=True)
    assert list(result.keys()) == ["ZEBRA", "MANGO", "ALPHA"]


def test_sort_by_value_ascending():
    with patch("envctl.env_sort.get_profile", side_effect=_mock_get), \
         patch("envctl.env_sort.set_profile", side_effect=_mock_set):
        result = sort_profile("dev", by="value")
    assert list(result.values()) == ["first", "last", "middle"]


def test_sort_missing_profile_raises():
    with patch("envctl.env_sort.get_profile", return_value=None):
        with pytest.raises(SortError, match="not found"):
            sort_profile("ghost")


def test_sort_persists_result():
    saved = {}

    def _capture_set(name, data):
        saved[name] = data

    with patch("envctl.env_sort.get_profile", side_effect=_mock_get), \
         patch("envctl.env_sort.set_profile", side_effect=_capture_set):
        sort_profile("dev", by="key")

    assert list(saved["dev"]["variables"].keys()) == ["ALPHA", "MANGO", "ZEBRA"]
