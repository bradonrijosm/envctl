"""Tests for envctl.env_check module."""

import pytest
from unittest.mock import patch

from envctl.env_check import (
    check_profile,
    check_all_profiles,
    check_empty_values,
    check_duplicate_values,
    EnvCheckError,
    CheckIssue,
)


MOD = "envctl.env_check"


def _mock_get(data):
    return patch(f"{MOD}.get_profile", return_value=data)


def _mock_load(data):
    return patch(f"{MOD}.load_profiles", return_value=data)


def test_check_empty_values_detects_empty():
    issues = check_empty_values("dev", {"KEY": "", "OTHER": "val"})
    assert len(issues) == 1
    assert issues[0].key == "KEY"
    assert issues[0].severity == "warning"


def test_check_empty_values_clean():
    issues = check_empty_values("dev", {"KEY": "value"})
    assert issues == []


def test_check_duplicate_values_detects_duplicates():
    issues = check_duplicate_values("dev", {"A": "same", "B": "same"})
    assert len(issues) == 1
    assert issues[0].key == "B"
    assert "A" in issues[0].message
    assert issues[0].severity == "warning"


def test_check_duplicate_values_no_duplicates():
    issues = check_duplicate_values("dev", {"A": "x", "B": "y"})
    assert issues == []


def test_check_duplicate_values_ignores_empty():
    issues = check_duplicate_values("dev", {"A": "", "B": ""})
    assert issues == []


def test_check_profile_missing_raises():
    with _mock_get(None):
        with pytest.raises(EnvCheckError, match="does not exist"):
            check_profile("ghost")


def test_check_profile_clean_returns_no_issues():
    with _mock_get({"KEY": "value", "OTHER": "different"}):
        result = check_profile("dev")
    assert result.profile == "dev"
    assert result.issues == []
    assert not result.has_errors()
    assert not result.has_warnings()


def test_check_profile_with_empty_value():
    with _mock_get({"KEY": "", "B": "val"}):
        result = check_profile("dev")
    assert result.has_warnings()
    assert any(i.key == "KEY" for i in result.issues)


def test_check_all_profiles_returns_results_for_each():
    profiles = {"dev": {"A": "1"}, "prod": {"B": "2"}}
    with _mock_load(profiles):
        with patch(f"{MOD}.get_profile", side_effect=lambda name, **kw: profiles[name]):
            results = check_all_profiles()
    assert len(results) == 2
    names = {r.profile for r in results}
    assert names == {"dev", "prod"}
