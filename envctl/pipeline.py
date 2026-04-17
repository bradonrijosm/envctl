"""Pipeline: apply a sequence of named operations to a profile."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List

from envctl.storage import get_profile, set_profile


class PipelineError(Exception):
    pass


# A step is a callable that receives and returns a variable dict.
StepFn = Callable[[Dict[str, str]], Dict[str, str]]


@dataclass
class Pipeline:
    name: str
    steps: List[tuple[str, StepFn]] = field(default_factory=list)

    def add_step(self, label: str, fn: StepFn) -> "Pipeline":
        self.steps.append((label, fn))
        return self

    def run(self, variables: Dict[str, str]) -> Dict[str, str]:
        current = dict(variables)
        for label, fn in self.steps:
            try:
                current = fn(current)
            except Exception as exc:
                raise PipelineError(f"Step '{label}' failed: {exc}") from exc
        return current


def apply_pipeline(profile_name: str, pipeline: Pipeline) -> Dict[str, str]:
    """Load a profile, run it through *pipeline*, and persist the result."""
    profile = get_profile(profile_name)
    if profile is None:
        raise PipelineError(f"Profile '{profile_name}' not found.")
    result = pipeline.run(profile)
    set_profile(profile_name, result)
    return result


# ── built-in step factories ──────────────────────────────────────────────────

def step_prefix_keys(prefix: str) -> StepFn:
    """Return a step that prepends *prefix* to every key."""
    def _step(variables: Dict[str, str]) -> Dict[str, str]:
        return {f"{prefix}{k}": v for k, v in variables.items()}
    return _step


def step_uppercase_values() -> StepFn:
    """Return a step that uppercases every value."""
    def _step(variables: Dict[str, str]) -> Dict[str, str]:
        return {k: v.upper() for k, v in variables.items()}
    return _step


def step_filter_keys(keep: List[str]) -> StepFn:
    """Return a step that keeps only the listed keys."""
    keep_set = set(keep)
    def _step(variables: Dict[str, str]) -> Dict[str, str]:
        return {k: v for k, v in variables.items() if k in keep_set}
    return _step
