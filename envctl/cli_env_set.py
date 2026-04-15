"""cli_env_set.py — CLI commands for bulk set/unset of profile variables."""

from __future__ import annotations

import click

from envctl.env_set import EnvSetError, bulk_set, bulk_unset


@click.group(name="var")
def cmd_var() -> None:
    """Manage individual variables within a profile."""


@cmd_var.command(name="set")
@click.argument("profile")
@click.argument("assignments", nargs=-1, required=True, metavar="KEY=VALUE...")
@click.option("--no-overwrite", is_flag=True, default=False, help="Skip keys that already exist.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without saving.")
def var_set(profile: str, assignments: tuple, no_overwrite: bool, dry_run: bool) -> None:
    """Set KEY=VALUE pairs in PROFILE."""
    variables: dict[str, str] = {}
    for assignment in assignments:
        if "=" not in assignment:
            raise click.BadParameter(f"Expected KEY=VALUE, got {assignment!r}")
        key, _, value = assignment.partition("=")
        variables[key.strip()] = value

    try:
        result = bulk_set(profile, variables, overwrite=not no_overwrite, dry_run=dry_run)
    except EnvSetError as exc:
        raise click.ClickException(str(exc)) from exc

    prefix = "[dry-run] " if dry_run else ""
    click.echo(f"{prefix}Profile {profile!r} — {len(variables)} variable(s) set.")
    for key in variables:
        click.echo(f"  {key}={result.get(key, '')}")


@cmd_var.command(name="unset")
@click.argument("profile")
@click.argument("keys", nargs=-1, required=True, metavar="KEY...")
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without saving.")
def var_unset(profile: str, keys: tuple, dry_run: bool) -> None:
    """Remove KEY(s) from PROFILE."""
    try:
        bulk_unset(profile, list(keys), dry_run=dry_run)
    except EnvSetError as exc:
        raise click.ClickException(str(exc)) from exc

    prefix = "[dry-run] " if dry_run else ""
    click.echo(f"{prefix}Profile {profile!r} — {len(keys)} variable(s) removed.")
    for key in keys:
        click.echo(f"  - {key}")
