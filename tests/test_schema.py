"""Tests for envctl.schema — schema definition and validation."""

import pytest

from envctl.schema import (
    SchemaError,
    delete_schema,
    get_schema,
    set_schema,
    validate_against_schema,
)
from envctl.storage import set_profile


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.storage.get_store_path", lambda: tmp_path)
    monkeypatch.setattr("envctl.schema.get_store_path", lambda: tmp_path)
    yield tmp_path


def _seed_profile(name: str, variables: dict) -> None:
    set_profile(name, variables)


# --- set_schema / get_schema ---

def test_set_and_get_schema():
    set_schema("prod", required=["DB_URL", "SECRET_KEY"], optional=["DEBUG"])
    schema = get_schema("prod")
    assert schema is not None
    assert schema["required"] == ["DB_URL", "SECRET_KEY"]
    assert schema["optional"] == ["DEBUG"]


def test_get_schema_missing_returns_none():
    assert get_schema("nonexistent") is None


def test_set_schema_overwrites_existing():
    set_schema("dev", required=["OLD_KEY"])
    set_schema("dev", required=["NEW_KEY"], optional=["EXTRA"])
    schema = get_schema("dev")
    assert schema["required"] == ["NEW_KEY"]
    assert schema["optional"] == ["EXTRA"]


# --- delete_schema ---

def test_delete_schema_removes_entry():
    set_schema("staging", required=["API_KEY"])
    delete_schema("staging")
    assert get_schema("staging") is None


def test_delete_schema_missing_raises():
    with pytest.raises(SchemaError, match="No schema found"):
        delete_schema("ghost")


# --- validate_against_schema ---

def test_validate_no_violations():
    _seed_profile("prod", {"DB_URL": "postgres://", "SECRET_KEY": "abc", "DEBUG": "false"})
    set_schema("prod", required=["DB_URL", "SECRET_KEY"], optional=["DEBUG"])
    violations = validate_against_schema("prod")
    assert violations == []


def test_validate_missing_required_key():
    _seed_profile("prod", {"DB_URL": "postgres://"})
    set_schema("prod", required=["DB_URL", "SECRET_KEY"])
    violations = validate_against_schema("prod")
    assert any("SECRET_KEY" in v for v in violations)


def test_validate_unexpected_key():
    _seed_profile("prod", {"DB_URL": "postgres://", "ROGUE": "value"})
    set_schema("prod", required=["DB_URL"], optional=[])
    violations = validate_against_schema("prod")
    assert any("ROGUE" in v for v in violations)


def test_validate_no_schema_raises():
    _seed_profile("dev", {"KEY": "val"})
    with pytest.raises(SchemaError, match="No schema defined"):
        validate_against_schema("dev")


def test_validate_missing_profile_raises():
    set_schema("ghost", required=["KEY"])
    with pytest.raises(SchemaError, match="does not exist"):
        validate_against_schema("ghost")


def test_validate_empty_schema_allows_any_keys():
    """An empty required+optional schema should report no violations."""
    _seed_profile("free", {"ANY_KEY": "value"})
    set_schema("free", required=[], optional=[])
    # allowed set is empty, so we skip unexpected-key checks
    violations = validate_against_schema("free")
    assert violations == []
