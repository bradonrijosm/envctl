"""Tests for envctl.export module."""

import pytest

from envctl.export import (
    ExportError,
    export_bash,
    export_dotenv,
    export_fish,
    export_profile,
)

SAMPLE_VARS = {"API_KEY": "abc123", "DEBUG": "true", "PORT": "8080"}


def test_export_bash_contains_export_statements():
    result = export_bash(SAMPLE_VARS, "dev")
    assert 'export API_KEY="abc123"' in result
    assert 'export PORT="8080"' in result
    assert "# envctl profile: dev" in result


def test_export_fish_uses_set_x():
    result = export_fish(SAMPLE_VARS, "staging")
    assert 'set -x API_KEY "abc123"' in result
    assert "# envctl profile: staging" in result


def test_export_dotenv_no_export_keyword():
    result = export_dotenv(SAMPLE_VARS, "prod")
    assert 'API_KEY="abc123"' in result
    assert "export" not in result
    assert "# envctl profile: prod" in result


def test_export_profile_bash_format():
    result = export_profile(SAMPLE_VARS, "dev", fmt="bash")
    assert 'export DEBUG="true"' in result


def test_export_profile_fish_format():
    result = export_profile(SAMPLE_VARS, "dev", fmt="fish")
    assert 'set -x DEBUG "true"' in result


def test_export_profile_dotenv_format():
    result = export_profile(SAMPLE_VARS, "dev", fmt="dotenv")
    assert 'DEBUG="true"' in result


def test_export_profile_invalid_format_raises():
    with pytest.raises(ExportError, match="Unsupported format"):
        export_profile(SAMPLE_VARS, "dev", fmt="powershell")


def test_export_escapes_double_quotes():
    vars_with_quotes = {"MSG": 'say "hello"'}
    result = export_bash(vars_with_quotes, "test")
    assert 'export MSG="say \\"hello\\""' in result


def test_export_profile_writes_to_file(tmp_path):
    out_file = tmp_path / "env.sh"
    export_profile(SAMPLE_VARS, "dev", fmt="bash", output_path=str(out_file))
    assert out_file.exists()
    content = out_file.read_text()
    assert 'export API_KEY="abc123"' in content


def test_export_variables_sorted_alphabetically():
    result = export_bash(SAMPLE_VARS, "dev")
    lines = [l for l in result.splitlines() if l.startswith("export")]
    keys = [l.split()[1].split("=")[0] for l in lines]
    assert keys == sorted(keys)
