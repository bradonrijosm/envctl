"""Tests for envctl.template module."""

import pytest
from unittest.mock import patch

from envctl.template import render_value, render_profile, TemplateError


FAKE_PROFILES = {
    "base": {"HOST": "localhost", "PORT": "5432"},
    "app": {"DB_URL": "postgres://{{base.HOST}}:{{base.PORT}}/mydb", "APP_HOST": "{{HOST}}"},
    "self_ref": {"HOST": "myhost", "URL": "http://{{HOST}}/path"},
    "broken": {"VAL": "{{MISSING_VAR}}"},
}


def test_render_value_no_template():
    result = render_value("plain_value", {}, {})
    assert result == "plain_value"


def test_render_value_current_profile_ref():
    context = {"HOST": "localhost"}
    result = render_value("http://{{HOST}}/api", context, {})
    assert result == "http://localhost/api"


def test_render_value_cross_profile_ref():
    all_profiles = {"base": {"PORT": "8080"}}
    result = render_value("{{base.PORT}}", {}, all_profiles)
    assert result == "8080"


def test_render_value_missing_var_raises():
    with pytest.raises(TemplateError, match="Undefined variable reference"):
        render_value("{{MISSING}}", {}, {})


def test_render_value_missing_profile_raises():
    with pytest.raises(TemplateError, match="Unknown profile in template reference"):
        render_value("{{ghost.VAR}}", {}, {})


def test_render_value_missing_var_in_known_profile_raises():
    all_profiles = {"base": {"HOST": "localhost"}}
    with pytest.raises(TemplateError, match="Variable 'MISSING' not found in profile 'base'"):
        render_value("{{base.MISSING}}", {}, all_profiles)


def test_render_profile_self_reference():
    with patch("envctl.template.load_profiles", return_value=FAKE_PROFILES):
        rendered = render_profile("self_ref")
    assert rendered["URL"] == "http://myhost/path"
    assert rendered["HOST"] == "myhost"


def test_render_profile_cross_profile_reference():
    with patch("envctl.template.load_profiles", return_value=FAKE_PROFILES):
        rendered = render_profile("app")
    assert rendered["DB_URL"] == "postgres://localhost:5432/mydb"


def test_render_profile_nonexistent_raises():
    with patch("envctl.template.load_profiles", return_value=FAKE_PROFILES):
        with pytest.raises(TemplateError, match="Profile 'nope' does not exist"):
            render_profile("nope")


def test_render_profile_broken_raises():
    with patch("envctl.template.load_profiles", return_value=FAKE_PROFILES):
        with pytest.raises(TemplateError, match="Undefined variable reference"):
            render_profile("broken")


def test_render_value_multiple_refs_in_one_value():
    context = {"USER": "admin", "PASS": "secret"}
    result = render_value("{{USER}}:{{PASS}}", context, {})
    assert result == "admin:secret"
