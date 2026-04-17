"""CLI command: envctl resolve <profile> — print fully resolved variables."""

import click
from envctl.env_resolve import resolve_to_env_dict, ResolveError


@click.group(name="resolve")
def cmd_resolve():
    """Resolve and display final variable values for a profile."""


@cmd_resolve.command(name="show")
@click.argument("profile")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["env", "export", "json"]),
    default="env",
    show_default=True,
    help="Output format.",
)
def resolve_show(profile: str, fmt: str):
    """Print resolved variables for PROFILE."""
    try:
        variables = resolve_to_env_dict(profile)
    except ResolveError as exc:
        raise click.ClickException(str(exc))

    if not variables:
        click.echo(f"(no variables in profile '{profile}')")
        return

    if fmt == "json":
        import json
        click.echo(json.dumps(variables, indent=2))
    elif fmt == "export":
        for k, v in sorted(variables.items()):
            click.echo(f"export {k}={v}")
    else:
        for k, v in sorted(variables.items()):
            click.echo(f"{k}={v}")
