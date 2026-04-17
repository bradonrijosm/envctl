"""Tests for envctl.env_diff_apply."""
import pytest
from unittest.mock import patch
from envctl.env_diff_apply import apply_diff, PatchError


SRC = {"A": "1", "B": "2", "C": "3"}
TGT = {"B": "99", "D": "4"}


def _mock_get(name):
    return {"src": dict(SRC), "tgt": dict(TGT)}.get(name)


@pytest.fixture(autouse=True)
def _patch_storage(monkeypatch):
    saved = {}

    def fake_set(name, data):
        saved[name] = data

    monkeypatch.setattr("envctl.env_diff_apply.get_profile", _mock_get)
    monkeypatch.setattr("envctl.env_diff_apply.set_profile", fake_set)
    monkeypatch.setattr(
        "envctl.diff.get_profile",
        _mock_get,
    )
    return saved


def test_apply_adds_source_only_keys(_patch_storage):
    result = apply_diff("src", "tgt", dry_run=True)
    assert result["A"] == "1"   # only in src -> added
    assert result["C"] == "3"   # only in src -> added


def test_apply_keeps_target_only_keys(_patch_storage):
    result = apply_diff("src", "tgt", dry_run=True)
    assert result["D"] == "4"   # only in tgt -> kept


def test_apply_no_overwrite_keeps_target_changed_value(_patch_storage):
    result = apply_diff("src", "tgt", overwrite=False, dry_run=True)
    assert result["B"] == "99"  # changed, no overwrite -> target wins


def test_apply_overwrite_replaces_changed_value(_patch_storage):
    result = apply_diff("src", "tgt", overwrite=True, dry_run=True)
    assert result["B"] == "2"   # changed, overwrite -> source wins


def test_apply_persists_when_not_dry_run(_patch_storage):
    apply_diff("src", "tgt", dry_run=False)
    assert "tgt" in _patch_storage


def test_apply_dry_run_does_not_persist(_patch_storage):
    apply_diff("src", "tgt", dry_run=True)
    assert "tgt" not in _patch_storage


def test_apply_missing_source_raises(_patch_storage):
    with pytest.raises(PatchError, match="Source"):
        apply_diff("missing", "tgt")


def test_apply_missing_target_raises(_patch_storage):
    with pytest.raises(PatchError, match="Target"):
        apply_diff("src", "missing")
