"""Tests for envctl.env_case — key/value case transformation."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envctl.env_case import (
    CaseError,
    transform_keys,
    transform_values,
    list_modes,
)


_BASE_VARS = {"db_host": "localhost", "db_port": "5432", "app_name": "envctl"}


def _mock_get(name):
    if name == "dev":
        return dict(_BASE_VARS)
    return None


def _mock_set(name, variables):
    pass


# ── list_modes ────────────────────────────────────────────────────────────────

def test_list_modes_returns_expected():
    modes = list_modes()
    assert "upper" in modes
    assert "lower" in modes
    assert "title" in modes


# ── transform_keys ────────────────────────────────────────────────────────────

@patch("envctl.env_case.set_profile", side_effect=_mock_set)
@patch("envctl.env_case.get_profile", side_effect=_mock_get)
def test_transform_keys_upper(mock_get, mock_set):
    result = transform_keys("dev", "upper")
    assert "DB_HOST" in result
    assert "DB_PORT" in result
    assert "APP_NAME" in result


@patch("envctl.env_case.set_profile", side_effect=_mock_set)
@patch("envctl.env_case.get_profile", side_effect=_mock_get)
def test_transform_keys_lower(mock_get, mock_set):
    result = transform_keys("dev", "lower")
    assert all(k == k.lower() for k in result)


@patch("envctl.env_case.set_profile", side_effect=_mock_set)
@patch("envctl.env_case.get_profile", side_effect=_mock_get)
def test_transform_keys_missing_profile_raises(mock_get, mock_set):
    with pytest.raises(CaseError, match="not found"):
        transform_keys("nonexistent", "upper")


@patch("envctl.env_case.set_profile", side_effect=_mock_set)
@patch("envctl.env_case.get_profile", side_effect=_mock_get)
def test_transform_keys_invalid_mode_raises(mock_get, mock_set):
    with pytest.raises(CaseError, match="Unknown mode"):
        transform_keys("dev", "camel")


# ── transform_values ──────────────────────────────────────────────────────────

@patch("envctl.env_case.set_profile", side_effect=_mock_set)
@patch("envctl.env_case.get_profile", side_effect=_mock_get)
def test_transform_values_upper(mock_get, mock_set):
    result = transform_values("dev", "upper")
    assert result["db_host"] == "LOCALHOST"
    assert result["app_name"] == "ENVCTL"


@patch("envctl.env_case.set_profile", side_effect=_mock_set)
@patch("envctl.env_case.get_profile", side_effect=_mock_get)
def test_transform_values_lower(mock_get, mock_set):
    result = transform_values("dev", "lower")
    assert all(v == v.lower() for v in result.values())


@patch("envctl.env_case.set_profile", side_effect=_mock_set)
@patch("envctl.env_case.get_profile", side_effect=_mock_get)
def test_transform_values_missing_profile_raises(mock_get, mock_set):
    with pytest.raises(CaseError, match="not found"):
        transform_values("ghost", "lower")


@patch("envctl.env_case.set_profile", side_effect=_mock_set)
@patch("envctl.env_case.get_profile", side_effect=_mock_get)
def test_transform_values_persists(mock_get, mock_set):
    transform_values("dev", "upper")
    assert mock_set.called
    call_args = mock_set.call_args
    assert call_args[0][0] == "dev"
