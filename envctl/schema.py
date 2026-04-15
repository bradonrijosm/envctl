"""Schema validation for environment variable profiles.

Allows users to define expected keys (required/optional) and simple
type hints for a profile, then validate an existing profile against it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envctl.storage import get_store_path, get_profile


class SchemaError(Exception):
    """Raised when schema operations fail."""


_SCHEMA_FILE = "schemas.json"


def _get_schema_path() -> Path:
    return get_store_path() / _SCHEMA_FILE


def _load_schemas() -> Dict[str, dict]:
    path = _get_schema_path()
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def _save_schemas(schemas: Dict[str, dict]) -> None:
    path = _get_schema_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(schemas, fh, indent=2)


def set_schema(profile_name: str, required: List[str], optional: Optional[List[str]] = None) -> None:
    """Attach a schema (required/optional key lists) to a profile name."""
    schemas = _load_schemas()
    schemas[profile_name] = {
        "required": list(required),
        "optional": list(optional or []),
    }
    _save_schemas(schemas)


def get_schema(profile_name: str) -> Optional[dict]:
    """Return the schema for *profile_name*, or None if not defined."""
    return _load_schemas().get(profile_name)


def delete_schema(profile_name: str) -> None:
    """Remove the schema for *profile_name*. Raises SchemaError if absent."""
    schemas = _load_schemas()
    if profile_name not in schemas:
        raise SchemaError(f"No schema found for profile '{profile_name}'.")
    del schemas[profile_name]
    _save_schemas(schemas)


def validate_against_schema(profile_name: str) -> List[str]:
    """Validate *profile_name* against its schema.

    Returns a (possibly empty) list of human-readable violation strings.
    Raises SchemaError if the profile or schema does not exist.
    """
    schema = get_schema(profile_name)
    if schema is None:
        raise SchemaError(f"No schema defined for profile '{profile_name}'.")

    profile = get_profile(profile_name)
    if profile is None:
        raise SchemaError(f"Profile '{profile_name}' does not exist.")

    violations: List[str] = []
    present_keys = set(profile.keys())

    for key in schema.get("required", []):
        if key not in present_keys:
            violations.append(f"Missing required key: {key}")

    allowed = set(schema.get("required", [])) | set(schema.get("optional", []))
    for key in present_keys:
        if allowed and key not in allowed:
            violations.append(f"Unexpected key not in schema: {key}")

    return violations
