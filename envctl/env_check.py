"""Check profiles for missing or undefined variable references."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from envctl.storage import get_profile, load_profiles


class EnvCheckError(Exception):
    pass


@dataclass
class CheckIssue:
    profile: str
    key: str
    message: str
    severity: str = "error"  # 'error' | 'warning'


@dataclass
class CheckResult:
    profile: str
    issues: List[CheckIssue] = field(default_factory=list)

    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)


def check_empty_values(profile_name: str, variables: Dict[str, str]) -> List[CheckIssue]:
    issues = []
    for key, value in variables.items():
        if value == "":
            issues.append(CheckIssue(profile=profile_name, key=key,
                                     message=f"Variable '{key}' is empty.",
                                     severity="warning"))
    return issues


def check_duplicate_values(profile_name: str, variables: Dict[str, str]) -> List[CheckIssue]:
    issues = []
    seen: Dict[str, str] = {}
    for key, value in variables.items():
        if value and value in seen:
            issues.append(CheckIssue(profile=profile_name, key=key,
                                     message=f"Variable '{key}' has duplicate value as '{seen[value]}'.",
                                     severity="warning"))
        elif value:
            seen[value] = key
    return issues


def check_profile(profile_name: str, store_path: Optional[str] = None) -> CheckResult:
    kwargs = {"store_path": store_path} if store_path else {}
    variables = get_profile(profile_name, **kwargs)
    if variables is None:
        raise EnvCheckError(f"Profile '{profile_name}' does not exist.")

    result = CheckResult(profile=profile_name)
    result.issues.extend(check_empty_values(profile_name, variables))
    result.issues.extend(check_duplicate_values(profile_name, variables))
    return result


def check_all_profiles(store_path: Optional[str] = None) -> List[CheckResult]:
    kwargs = {"store_path": store_path} if store_path else {}
    profiles = load_profiles(**kwargs)
    return [check_profile(name, store_path=store_path) for name in profiles]
