"""Tests for envctl.validate module."""

import pytest
from envctl.validate import (
    ValidationError,
    is_valid_var_name,
    is_valid_profile_name,
    validate_variables,
    validate_profile_name,
)


# --- is_valid_var_name ---

def test_valid_var_names():
    assert is_valid_var_name('FOO') is True
    assert is_valid_var_name('foo_bar') is True
    assert is_valid_var_name('_PRIVATE') is True
    assert is_valid_var_name('VAR123') is True


def test_invalid_var_names():
    assert is_valid_var_name('') is False
    assert is_valid_var_name('123ABC') is False
    assert is_valid_var_name('FOO-BAR') is False
    assert is_valid_var_name('FOO BAR') is False
    assert is_valid_var_name('FOO=BAR') is False


# --- is_valid_profile_name ---

def test_valid_profile_names():
    assert is_valid_profile_name('dev') is True
    assert is_valid_profile_name('prod-us-east') is True
    assert is_valid_profile_name('staging.v2') is True
    assert is_valid_profile_name('A' * 64) is True


def test_invalid_profile_names():
    assert is_valid_profile_name('') is False
    assert is_valid_profile_name('my profile') is False
    assert is_valid_profile_name('A' * 65) is False
    assert is_valid_profile_name('name!') is False


# --- validate_variables ---

def test_validate_variables_ok():
    validate_variables({'API_KEY': 'abc', 'DEBUG': 'true'})  # should not raise


def test_validate_variables_invalid_name_raises():
    with pytest.raises(ValidationError) as exc_info:
        validate_variables({'INVALID-NAME': 'value', 'GOOD': 'ok'})
    assert 'INVALID-NAME' in exc_info.value.invalid_keys


def test_validate_variables_reserved_raises():
    with pytest.raises(ValidationError) as exc_info:
        validate_variables({'PATH': '/usr/bin', 'APP': 'myapp'})
    assert 'PATH' in exc_info.value.invalid_keys


def test_validate_variables_reserved_allowed_when_flag_set():
    validate_variables({'PATH': '/usr/bin'}, allow_reserved=True)  # should not raise


def test_validate_variables_multiple_invalid_keys_reported():
    with pytest.raises(ValidationError) as exc_info:
        validate_variables({'1BAD': 'x', '2BAD': 'y', 'GOOD': 'ok'})
    assert len(exc_info.value.invalid_keys) == 2


# --- validate_profile_name ---

def test_validate_profile_name_ok():
    validate_profile_name('my-profile')  # should not raise


def test_validate_profile_name_invalid_raises():
    with pytest.raises(ValidationError, match="Invalid profile name"):
        validate_profile_name('bad name!')
