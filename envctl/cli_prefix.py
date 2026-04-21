"""CLI commands for adding/stripping key prefixes in a profile."""

import click

from envctl.env_prefix import PrefixError, add_prefix, strip_prefix


@click.group("prefix")
def cmd_prefix():
    """Add or strip a key prefix across a profile's variables."""


@cmd_prefix.command("add")
@click.argument("profile")
@click.argument("prefix")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Allow overwriting keys that already carry the prefix.",
)
def prefix_add(profile: str, prefix: str, overwrite: bool):
    """Prepend PREFIX to every variable key in PROFILE."""
    try:
        updated = add_prefix(profile, prefix, overwrite=overwrite)
        click.echo(f"Added prefix '{prefix}' to {len(updated)} key(s) in '{profile}'.")
    except PrefixError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_prefix.command("strip")
@click.argument("profile")
@click.argument("prefix")
@click.option(
    "--ignore-missing",
    is_flag=True,
    default=False,
    help="Silently skip keys that do not start with the prefix.",
)
def prefix_strip(profile: str, prefix: str, ignore_missing: bool):
    """Remove PREFIX from the start of every variable key in PROFILE."""
    try:
        updated = strip_prefix(profile, prefix, ignore_missing=ignore_missing)
        click.echo(f"Stripped prefix '{prefix}' from keys in '{profile}'. {len(updated)} key(s) remain.")
    except PrefixError as exc:
        raise click.ClickException(str(exc)) from exc
