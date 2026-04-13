"""Import environment variables from .env or shell export files into a profile."""

import re
from typing import Dict, Tuple


class ImportError(Exception):  # noqa: A001
    """Raised when import parsing fails."""


def parse_dotenv(content: str) -> Dict[str, str]:
    """Parse a .env-style file into a dict of key/value pairs.

    Supports:
    - KEY=VALUE
    - KEY="VALUE"
    - KEY='VALUE'
    - Lines starting with # are comments
    - Blank lines are ignored
    """
    variables: Dict[str, str] = {}
    for lineno, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(
            r'^([A-Za-z_][A-Za-z0-9_]*)=(["\']?)(.*)\2$', line
        )
        if not match:
            raise ImportError(
                f"Line {lineno}: cannot parse variable assignment: {raw_line!r}"
            )
        key, _, value = match.group(1), match.group(2), match.group(3)
        variables[key] = value
    return variables


def parse_bash_exports(content: str) -> Dict[str, str]:
    """Parse bash 'export KEY="VALUE"' lines into a dict."""
    variables: Dict[str, str] = {}
    for lineno, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(
            r'^export\s+([A-Za-z_][A-Za-z0-9_]*)=(["\']?)(.*)\2$', line
        )
        if not match:
            raise ImportError(
                f"Line {lineno}: cannot parse export statement: {raw_line!r}"
            )
        key, value = match.group(1), match.group(3)
        variables[key] = value
    return variables


def load_from_file(file_path: str) -> Tuple[Dict[str, str], str]:
    """Auto-detect format and parse variables from a file.

    Returns (variables_dict, detected_format).
    """
    with open(file_path) as fh:
        content = fh.read()

    # Detect format by scanning for export keyword
    has_export = any(
        line.strip().startswith("export ")
        for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#")
    )
    if has_export:
        return parse_bash_exports(content), "bash"
    return parse_dotenv(content), "dotenv"
