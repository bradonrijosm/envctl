"""Tests for envctl.pipeline."""
import pytest

from envctl.pipeline import (
    Pipeline,
    PipelineError,
    apply_pipeline,
    step_filter_keys,
    step_prefix_keys,
    step_uppercase_values,
)
from envctl.storage import get_profile, set_profile


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVCTL_STORE", str(tmp_path / "store.json"))


def _seed(name: str, variables: dict):
    set_profile(name, variables)


# ── step unit tests ──────────────────────────────────────────────────────────

def test_step_prefix_keys_adds_prefix():
    fn = step_prefix_keys("APP_")
    result = fn({"FOO": "bar", "BAZ": "qux"})
    assert result == {"APP_FOO": "bar", "APP_BAZ": "qux"}


def test_step_uppercase_values():
    fn = step_uppercase_values()
    result = fn({"KEY": "hello", "OTHER": "world"})
    assert result == {"KEY": "HELLO", "OTHER": "WORLD"}


def test_step_filter_keys_keeps_only_listed():
    fn = step_filter_keys(["A", "C"])
    result = fn({"A": "1", "B": "2", "C": "3"})
    assert result == {"A": "1", "C": "3"}


def test_step_filter_keys_missing_keys_ignored():
    fn = step_filter_keys(["X"])
    result = fn({"A": "1"})
    assert result == {}


# ── Pipeline.run ─────────────────────────────────────────────────────────────

def test_pipeline_runs_steps_in_order():
    pipeline = (
        Pipeline("test")
        .add_step("upper", step_uppercase_values())
        .add_step("prefix", step_prefix_keys("P_"))
    )
    result = pipeline.run({"key": "val"})
    assert result == {"P_KEY": "VAL"}


def test_pipeline_step_failure_raises_pipeline_error():
    def bad_step(v):
        raise RuntimeError("boom")

    pipeline = Pipeline("bad").add_step("boom", bad_step)
    with pytest.raises(PipelineError, match="boom"):
        pipeline.run({"K": "V"})


# ── apply_pipeline ────────────────────────────────────────────────────────────

def test_apply_pipeline_persists_result():
    _seed("dev", {"HOST": "localhost"})
    pipeline = Pipeline("p").add_step("upper", step_uppercase_values())
    apply_pipeline("dev", pipeline)
    assert get_profile("dev") == {"HOST": "LOCALHOST"}


def test_apply_pipeline_missing_profile_raises():
    pipeline = Pipeline("p").add_step("upper", step_uppercase_values())
    with pytest.raises(PipelineError, match="not found"):
        apply_pipeline("ghost", pipeline)


def test_apply_pipeline_returns_transformed_vars():
    _seed("prod", {"A": "1", "B": "2", "C": "3"})
    pipeline = Pipeline("p").add_step("filter", step_filter_keys(["A", "C"]))
    result = apply_pipeline("prod", pipeline)
    assert result == {"A": "1", "C": "3"}
