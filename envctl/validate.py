"""Validation utilities for environment variable profiles."""

import re
from typing import Dict, List

# Valid shell variable name pattern
_VAR_NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

# Reserved variable names that should not be overwritten
_RESERVED_VARS = frozenset({
    'PATH', 'HOME', 'USER', 'SHELL', 'PWD', 'OLDPWD',
    'IFS', 'PS1', 'PS2', 'TERM', 'LANG', 'LC_ALL',
})


class ValidationError(Exception):
    """Raised when profile or variable validation fails."""

    def __init__(self, message: str, invalid_keys: List[str] = None):
        super().__init__(message)
        self.invalid_keys = invalid_keys or []


def is_valid_var_name(name: str) -> bool:
    """Return True if *name* is a valid shell variable name."""
    return bool(_VAR_NAME_RE.match(name))


def is_valid_profile_name(name: str) -> bool:
    """Return True if *name* is a valid profile identifier."""
    return bool(re.match(r'^[A-Za-z0-9_\-\.]+$', name)) and len(name) <= 64


def validate_variables(variables: Dict[str, str], *, allow_reserved: bool = False) -> None:
    """Validate a dict of variable names and values.

    Raises ValidationError if any key is not a valid shell variable name,
    or if a reserved variable is present and *allow_reserved* is False.
    """
    invalid_names: List[str] = []
    reserved_found: List[str] = []

    for key in variables:
        if not is_valid_var_name(key):
            invalid_names.append(key)
        elif not allow_reserved and key in _RESERVED_VARS:
            reserved_found.append(key)

    if invalid_names:
        raise ValidationError(
            f"Invalid variable name(s): {', '.join(sorted(invalid_names))}",
            invalid_keys=invalid_names,
        )

    if reserved_found:
        raise ValidationError(
            f"Reserved variable(s) cannot be set: {', '.join(sorted(reserved_found))}. "
            "Use --allow-reserved to override.",
            invalid_keys=reserved_found,
        )


def validate_profile_name(name: str) -> None:
    """Raise ValidationError if *name* is not a valid profile identifier."""
    if not is_valid_profile_name(name):
        raise ValidationError(
            f"Invalid profile name '{name}'. "
            "Use only letters, digits, hyphens, underscores, and dots (max 64 chars)."
        )
