"""Tests for envctl.import_env module."""

import pytest

from envctl.import_env import ImportError, load_from_file, parse_bash_exports, parse_dotenv


def test_parse_dotenv_simple():
    content = "KEY=value\nFOO=bar\n"
    result = parse_dotenv(content)
    assert result == {"KEY": "value", "FOO": "bar"}


def test_parse_dotenv_quoted_double():
    content = 'API_KEY="abc123"\n'
    result = parse_dotenv(content)
    assert result["API_KEY"] == "abc123"


def test_parse_dotenv_quoted_single():
    content = "SECRET='my secret'\n"
    result = parse_dotenv(content)
    assert result["SECRET"] == "my secret"


def test_parse_dotenv_ignores_comments_and_blanks():
    content = "# comment\n\nKEY=val\n"
    result = parse_dotenv(content)
    assert result == {"KEY": "val"}


def test_parse_dotenv_invalid_line_raises():
    with pytest.raises(ImportError, match="cannot parse"):
        parse_dotenv("NOT_VALID_LINE\n")


def test_parse_bash_exports_basic():
    content = 'export FOO="bar"\nexport BAZ="qux"\n'
    result = parse_bash_exports(content)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_bash_exports_ignores_comments():
    content = "# envctl profile: dev\nexport KEY=\"val\"\n"
    result = parse_bash_exports(content)
    assert result == {"KEY": "val"}


def test_parse_bash_exports_invalid_raises():
    with pytest.raises(ImportError, match="cannot parse"):
        parse_bash_exports("export BADLINE\n")


def test_load_from_file_detects_dotenv(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text('DB_URL="postgres://localhost/db"\nDEBUG=true\n')
    variables, fmt = load_from_file(str(env_file))
    assert fmt == "dotenv"
    assert variables["DEBUG"] == "true"


def test_load_from_file_detects_bash(tmp_path):
    env_file = tmp_path / "env.sh"
    env_file.write_text('export DB_URL="postgres://localhost/db"\nexport DEBUG="true"\n')
    variables, fmt = load_from_file(str(env_file))
    assert fmt == "bash"
    assert variables["DEBUG"] == "true"


def test_load_from_file_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_from_file(str(tmp_path / "nonexistent.env"))
