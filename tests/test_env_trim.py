"""Tests for envctl.env_trim."""

from __future__ import annotations

import pytest

from envctl.env_trim import TrimError, trim_all_profiles, trim_profile


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    """Redirect the store to a temporary directory for every test."""
    monkeypatch.setenv("ENVCTL_STORE_DIR", str(tmp_path))
    yield tmp_path


def _seed(name: str, variables: dict) -> None:
    from envctl.storage import set_profile
    set_profile(name, variables)


# ---------------------------------------------------------------------------
# trim_profile
# ---------------------------------------------------------------------------

def test_trim_profile_strips_spaces():
    _seed("dev", {"KEY": "  hello  ", "OTHER": "clean"})
    changed = trim_profile("dev")
    assert changed == {"KEY": "hello"}


def test_trim_profile_persists_to_store():
    from envctl.storage import get_profile
    _seed("dev", {"KEY": "  hello  "})
    trim_profile("dev")
    assert get_profile("dev") == {"KEY": "hello"}


def test_trim_profile_returns_empty_when_clean():
    _seed("dev", {"KEY": "clean"})
    changed = trim_profile("dev")
    assert changed == {}


def test_trim_profile_strips_tabs_and_newlines():
    _seed("dev", {"KEY": "\t value \n"})
    changed = trim_profile("dev")
    assert changed == {"KEY": "value"}


def test_trim_profile_missing_raises():
    with pytest.raises(TrimError, match="does not exist"):
        trim_profile("ghost")


def test_trim_profile_specific_keys_only():
    from envctl.storage import get_profile
    _seed("dev", {"A": "  a  ", "B": "  b  "})
    changed = trim_profile("dev", keys=["A"])
    assert changed == {"A": "a"}
    # B should be untouched
    assert get_profile("dev")["B"] == "  b  "


def test_trim_profile_specific_key_not_present_is_ignored():
    _seed("dev", {"A": "  a  "})
    changed = trim_profile("dev", keys=["MISSING"])
    assert changed == {}


def test_trim_profile_dry_run_does_not_persist():
    from envctl.storage import get_profile
    _seed("dev", {"KEY": "  hello  "})
    changed = trim_profile("dev", dry_run=True)
    assert changed == {"KEY": "hello"}
    # Store must remain unchanged
    assert get_profile("dev") == {"KEY": "  hello  "}


# ---------------------------------------------------------------------------
# trim_all_profiles
# ---------------------------------------------------------------------------

def test_trim_all_profiles_covers_multiple():
    _seed("dev", {"X": " x "})
    _seed("prod", {"Y": " y "})
    results = trim_all_profiles()
    assert results == {"dev": {"X": "x"}, "prod": {"Y": "y"}}


def test_trim_all_profiles_skips_clean():
    _seed("dev", {"X": "clean"})
    _seed("prod", {"Y": " dirty "})
    results = trim_all_profiles()
    assert "dev" not in results
    assert "prod" in results


def test_trim_all_profiles_dry_run():
    from envctl.storage import get_profile
    _seed("dev", {"X": " x "})
    results = trim_all_profiles(dry_run=True)
    assert results == {"dev": {"X": "x"}}
    assert get_profile("dev") == {"X": " x "}
