"""Export environment profiles to various shell formats."""

from typing import Dict, Optional

SUPPORTED_FORMATS = ("bash", "fish", "dotenv")


class ExportError(Exception):
    """Raised when export fails."""


def export_bash(variables: Dict[str, str], profile_name: str) -> str:
    """Export variables as bash export statements."""
    lines = [f"# envctl profile: {profile_name}"]
    for key, value in sorted(variables.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines) + "\n"


def export_fish(variables: Dict[str, str], profile_name: str) -> str:
    """Export variables as fish shell set statements."""
    lines = [f"# envctl profile: {profile_name}"]
    for key, value in sorted(variables.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'set -x {key} "{escaped}"')
    return "\n".join(lines) + "\n"


def export_dotenv(variables: Dict[str, str], profile_name: str) -> str:
    """Export variables in .env file format."""
    lines = [f"# envctl profile: {profile_name}"]
    for key, value in sorted(variables.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + "\n"


def export_profile(
    variables: Dict[str, str],
    profile_name: str,
    fmt: str = "bash",
    output_path: Optional[str] = None,
) -> str:
    """Export a profile's variables to the given format.

    Returns the rendered string and optionally writes to output_path.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ExportError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    renderers = {
        "bash": export_bash,
        "fish": export_fish,
        "dotenv": export_dotenv,
    }
    content = renderers[fmt](variables, profile_name)

    if output_path:
        with open(output_path, "w") as fh:
            fh.write(content)

    return content
