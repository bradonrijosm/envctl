"""Tests for envctl.lint."""

import pytest

from envctl.lint import LintError, LintResult, lint_all, lint_profile
from envctl.storage import save_profiles


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCTL_STORE", str(tmp_path / "store.json"))
    yield


def _seed(profiles: dict):
    save_profiles(profiles)


# ---------------------------------------------------------------------------
# lint_profile – basic happy path
# ---------------------------------------------------------------------------

def test_lint_clean_profile_has_no_issues():
    _seed({"prod": {"API_KEY": "abc123", "HOST": "example.com"}})
    result = lint_profile("prod")
    assert isinstance(result, LintResult)
    assert result.issues == []
    assert not result.has_errors
    assert not result.has_warnings


def test_lint_missing_profile_raises():
    _seed({})
    with pytest.raises(LintError, match="does not exist"):
        lint_profile("ghost")


def test_lint_invalid_profile_name_raises():
    with pytest.raises(LintError, match="Invalid profile name"):
        lint_profile("bad name!")


# ---------------------------------------------------------------------------
# W003 – empty profile
# ---------------------------------------------------------------------------

def test_lint_empty_profile_warns():
    _seed({"empty": {}})
    result = lint_profile("empty")
    codes = [i.code for i in result.issues]
    assert "W003" in codes


# ---------------------------------------------------------------------------
# W001 – empty value
# ---------------------------------------------------------------------------

def test_lint_empty_value_warns():
    _seed({"dev": {"TOKEN": ""}})
    result = lint_profile("dev")
    codes = [i.code for i in result.issues]
    assert "W001" in codes


# ---------------------------------------------------------------------------
# W002 – unexpanded shell variable
# ---------------------------------------------------------------------------

def test_lint_dollar_in_value_warns():
    _seed({"dev": {"PATH_EXT": "$HOME/bin"}})
    result = lint_profile("dev")
    codes = [i.code for i in result.issues]
    assert "W002" in codes


# ---------------------------------------------------------------------------
# I001 – lowercase key convention
# ---------------------------------------------------------------------------

def test_lint_lowercase_key_info():
    _seed({"dev": {"debug": "true"}})
    result = lint_profile("dev")
    codes = [i.code for i in result.issues]
    assert "I001" in codes


# ---------------------------------------------------------------------------
# lint_all
# ---------------------------------------------------------------------------

def test_lint_all_returns_result_per_profile():
    _seed({"a": {"X": "1"}, "b": {"Y": "2"}})
    results = lint_all()
    names = {r.profile_name for r in results}
    assert names == {"a", "b"}


def test_lint_all_empty_store_returns_empty_list():
    _seed({})
    assert lint_all() == []
