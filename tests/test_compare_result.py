"""Unit tests for CompareResult dataclass helpers."""

from envctl.compare import CompareResult


def _make(only_a=None, only_b=None, same=None, diff=None):
    return CompareResult(
        profile_a="a",
        profile_b="b",
        only_in_a=only_a or {},
        only_in_b=only_b or {},
        in_both_same=same or {},
        in_both_different=diff or {},
    )


def test_are_identical_true():
    r = _make(same={"X": "1"})
    assert r.are_identical is True


def test_are_identical_false_only_a():
    r = _make(only_a={"X": "1"})
    assert r.are_identical is False


def test_are_identical_false_only_b():
    r = _make(only_b={"X": "1"})
    assert r.are_identical is False


def test_are_identical_false_different():
    r = _make(diff={"X": ("a", "b")})
    assert r.are_identical is False


def test_similarity_pct_all_same():
    r = _make(same={"X": "1", "Y": "2"})
    assert r.similarity_pct == 100.0


def test_similarity_pct_none_same():
    r = _make(only_a={"X": "1"}, only_b={"Y": "2"})
    assert r.similarity_pct == 0.0


def test_similarity_pct_empty_profiles():
    r = _make()
    assert r.similarity_pct == 100.0


def test_similarity_pct_mixed():
    # 2 same, 1 diff, 1 only_a  => total 4, same 2 => 50%
    r = _make(
        same={"A": "1", "B": "2"},
        diff={"C": ("old", "new")},
        only_a={"D": "x"},
    )
    assert r.similarity_pct == 50.0
