"""Tests for envctl.env_resolve."""

import pytest
from unittest.mock import patch
from envctl.env_resolve import resolve_profile_name, resolve_profile_vars, ResolveError


PROFILES = {
    "base": {"HOST": "localhost", "PORT": "5432"},
    "prod": {"HOST": "prod.example.com", "PORT": "5432"},
}


def _mock_get(name, **_):
    return PROFILES.get(name)


def _mock_load(**_):
    return PROFILES


def _mock_render(name, all_profiles):
    return all_profiles.get(name, {})


def test_resolve_profile_name_no_alias():
    with patch("envctl.env_resolve.resolve_alias", side_effect=Exception("no alias")):
        result = resolve_profile_name("base")
    assert result == "base"


def test_resolve_profile_name_with_alias():
    with patch("envctl.env_resolve.resolve_alias", return_value="prod"):
        result = resolve_profile_name("p")
    assert result == "prod"


def test_resolve_profile_vars_success():
    with patch("envctl.env_resolve.resolve_alias", side_effect=Exception), \
         patch("envctl.env_resolve.get_profile", side_effect=_mock_get), \
         patch("envctl.env_resolve.load_profiles", side_effect=_mock_load), \
         patch("envctl.env_resolve.render_profile", side_effect=_mock_render):
        result = resolve_profile_vars("base")
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"


def test_resolve_profile_vars_missing_raises():
    with patch("envctl.env_resolve.resolve_alias", side_effect=Exception), \
         patch("envctl.env_resolve.get_profile", return_value=None), \
         patch("envctl.env_resolve.load_profiles", side_effect=_mock_load):
        with pytest.raises(ResolveError, match="not found"):
            resolve_profile_vars("ghost")


def test_resolve_profile_vars_template_error_raises():
    from envctl.template import TemplateError
    with patch("envctl.env_resolve.resolve_alias", side_effect=Exception), \
         patch("envctl.env_resolve.get_profile", side_effect=_mock_get), \
         patch("envctl.env_resolve.load_profiles", side_effect=_mock_load), \
         patch("envctl.env_resolve.render_profile", side_effect=TemplateError("bad ref")):
        with pytest.raises(ResolveError, match="bad ref"):
            resolve_profile_vars("base")


def test_resolve_to_env_dict_returns_plain_dict():
    with patch("envctl.env_resolve.resolve_alias", side_effect=Exception), \
         patch("envctl.env_resolve.get_profile", side_effect=_mock_get), \
         patch("envctl.env_resolve.load_profiles", side_effect=_mock_load), \
         patch("envctl.env_resolve.render_profile", side_effect=_mock_render):
        from envctl.env_resolve import resolve_to_env_dict
        result = resolve_to_env_dict("prod")
    assert isinstance(result, dict)
    assert result["HOST"] == "prod.example.com"
