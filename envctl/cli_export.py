"""CLI commands for exporting and importing environment profiles."""

import sys

import click

from envctl.export import ExportError, export_profile
from envctl.import_env import ImportError as EnvImportError
from envctl.import_env import load_from_file
from envctl.profiles import ProfileError, create_profile, get_profile, update_profile


@click.command("export")
@click.argument("profile_name")
@click.option(
    "--format", "fmt",
    default="bash",
    show_default=True,
    type=click.Choice(["bash", "fish", "dotenv"], case_sensitive=False),
    help="Output format.",
)
@click.option(
    "--output", "-o",
    default=None,
    metavar="FILE",
    help="Write output to FILE instead of stdout.",
)
def cmd_export(profile_name: str, fmt: str, output: str) -> None:
    """Export a profile's variables to shell format."""
    profile = get_profile(profile_name)
    if profile is None:
        click.echo(f"Error: profile '{profile_name}' not found.", err=True)
        sys.exit(1)
    try:
        content = export_profile(profile["variables"], profile_name, fmt=fmt, output_path=output)
    except ExportError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if output:
        click.echo(f"Profile '{profile_name}' exported to '{output}' ({fmt} format).")
    else:
        click.echo(content, nl=False)


@click.command("import")
@click.argument("profile_name")
@click.argument("file", type=click.Path(exists=True, readable=True))
@click.option(
    "--merge", is_flag=True, default=False,
    help="Merge into existing profile instead of replacing.",
)
def cmd_import(profile_name: str, file: str, merge: bool) -> None:
    """Import variables from a .env or shell file into a profile."""
    try:
        variables, detected_fmt = load_from_file(file)
    except EnvImportError as exc:
        click.echo(f"Parse error: {exc}", err=True)
        sys.exit(1)

    existing = get_profile(profile_name)
    try:
        if existing is None:
            create_profile(profile_name, variables)
            click.echo(
                f"Created profile '{profile_name}' with {len(variables)} variable(s) "
                f"from {file} (detected: {detected_fmt})."
            )
        else:
            update_profile(profile_name, variables, merge=merge)
            action = "Merged" if merge else "Updated"
            click.echo(
                f"{action} profile '{profile_name}' with {len(variables)} variable(s) "
                f"from {file} (detected: {detected_fmt})."
            )
    except ProfileError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
