"""Lint profiles for common issues: unused vars, shadowed keys, naming conventions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envctl.storage import get_profile, load_profiles
from envctl.validate import is_valid_var_name, is_valid_profile_name


class LintError(Exception):
    """Raised when a profile cannot be linted (e.g. not found)."""


@dataclass
class LintIssue:
    severity: str  # "error" | "warning" | "info"
    code: str
    message: str


@dataclass
class LintResult:
    profile_name: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)


def lint_profile(profile_name: str) -> LintResult:
    """Run all lint checks against a named profile and return a LintResult."""
    if not is_valid_profile_name(profile_name):
        raise LintError(f"Invalid profile name: {profile_name!r}")

    variables = get_profile(profile_name)
    if variables is None:
        raise LintError(f"Profile {profile_name!r} does not exist.")

    result = LintResult(profile_name=profile_name)

    for key, value in variables.items():
        # E001 – key does not match POSIX variable naming rules
        if not is_valid_var_name(key):
            result.issues.append(
                LintIssue("error", "E001", f"Variable name {key!r} is not a valid identifier.")
            )

        # W001 – empty value
        if value == "":
            result.issues.append(
                LintIssue("warning", "W001", f"{key!r} has an empty value.")
            )

        # W002 – value looks like an unexpanded shell variable
        if "$" in value:
            result.issues.append(
                LintIssue("warning", "W002", f"{key!r} value contains '$' which may be an unexpanded reference.")
            )

        # I001 – key is lowercase (convention: env vars should be uppercase)
        if key == key.lower() and key.replace("_", "").isalpha():
            result.issues.append(
                LintIssue("info", "I001", f"{key!r} is lowercase; environment variables are conventionally uppercase.")
            )

    # W003 – profile is empty
    if not variables:
        result.issues.append(
            LintIssue("warning", "W003", "Profile has no variables defined.")
        )

    return result


def lint_all() -> List[LintResult]:
    """Lint every profile in the store and return results for all."""
    profiles = load_profiles()
    return [lint_profile(name) for name in profiles]
