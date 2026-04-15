"""Tests for envctl.compare."""

import pytest

from envctl.compare import CompareError, CompareResult, compare_profiles, format_compare
from envctl.storage import save_profiles


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    store = tmp_path / "profiles.json"
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: store)
    monkeypatch.setattr("envctl.compare.get_profile", _get_profile_patched(store))
    return store


def _get_profile_patched(store):
    """Return a get_profile that reads from the tmp store."""
    from envctl import storage
    return storage.get_profile


def _seed(store, profiles):
    save_profiles(profiles)


def test_compare_identical_profiles(isolated_store):
    _seed(isolated_store, {"a": {"X": "1", "Y": "2"}, "b": {"X": "1", "Y": "2"}})
    result = compare_profiles("a", "b")
    assert result.are_identical
    assert result.similarity_pct == 100.0


def test_compare_only_in_a(isolated_store):
    _seed(isolated_store, {"a": {"X": "1", "EXTRA": "hi"}, "b": {"X": "1"}})
    result = compare_profiles("a", "b")
    assert "EXTRA" in result.only_in_a
    assert not result.only_in_b


def test_compare_only_in_b(isolated_store):
    _seed(isolated_store, {"a": {"X": "1"}, "b": {"X": "1", "NEW": "val"}})
    result = compare_profiles("a", "b")
    assert "NEW" in result.only_in_b
    assert not result.only_in_a


def test_compare_changed_key(isolated_store):
    _seed(isolated_store, {"a": {"X": "old"}, "b": {"X": "new"}})
    result = compare_profiles("a", "b")
    assert "X" in result.in_both_different
    assert result.in_both_different["X"] == ("old", "new")


def test_compare_missing_profile_a_raises(isolated_store):
    _seed(isolated_store, {"b": {"X": "1"}})
    with pytest.raises(CompareError, match="'ghost'"):
        compare_profiles("ghost", "b")


def test_compare_missing_profile_b_raises(isolated_store):
    _seed(isolated_store, {"a": {"X": "1"}})
    with pytest.raises(CompareError, match="'ghost'"):
        compare_profiles("a", "ghost")


def test_similarity_pct_partial(isolated_store):
    _seed(isolated_store, {"a": {"X": "1", "Y": "2"}, "b": {"X": "1", "Y": "99"}})
    result = compare_profiles("a", "b")
    # 1 same out of 2 total unique keys
    assert result.similarity_pct == 50.0


def test_format_compare_identical(isolated_store):
    _seed(isolated_store, {"a": {"K": "v"}, "b": {"K": "v"}})
    result = compare_profiles("a", "b")
    lines = format_compare(result)
    assert len(lines) == 1
    assert "identical" in lines[0]


def test_format_compare_shows_diff(isolated_store):
    _seed(isolated_store, {"a": {"X": "1"}, "b": {"X": "2", "Z": "3"}})
    result = compare_profiles("a", "b")
    text = "\n".join(format_compare(result))
    assert "changed" in text
    assert "only in b" in text
