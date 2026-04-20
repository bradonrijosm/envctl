"""cli_trim.py — CLI commands for trimming whitespace from profile values."""

from __future__ import annotations

import click

from envctl.env_trim import TrimError, trim_all_profiles, trim_profile


@click.group(name="trim")
def cmd_trim() -> None:
    """Trim leading/trailing whitespace from variable values."""


@cmd_trim.command(name="run")
@click.argument("profile")
@click.option(
    "--key",
    "keys",
    multiple=True,
    metavar="KEY",
    help="Limit trimming to specific keys (repeatable).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview changes without modifying the store.",
)
def trim_run(profile: str, keys: tuple[str, ...], dry_run: bool) -> None:
    """Trim whitespace in PROFILE."""
    try:
        changed = trim_profile(
            profile,
            keys=list(keys) if keys else None,
            dry_run=dry_run,
        )
    except TrimError as exc:
        raise click.ClickException(str(exc)) from exc

    if not changed:
        click.echo("No values needed trimming.")
        return

    prefix = "[dry-run] " if dry_run else ""
    for key, value in sorted(changed.items()):
        click.echo(f"{prefix}{key} -> {value!r}")

    if not dry_run:
        click.echo(f"Trimmed {len(changed)} value(s) in '{profile}'.")


@cmd_trim.command(name="all")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview changes without modifying the store.",
)
def trim_all(dry_run: bool) -> None:
    """Trim whitespace across ALL profiles."""
    results = trim_all_profiles(dry_run=dry_run)

    if not results:
        click.echo("No values needed trimming.")
        return

    prefix = "[dry-run] " if dry_run else ""
    total = 0
    for profile_name, changed in sorted(results.items()):
        for key, value in sorted(changed.items()):
            click.echo(f"{prefix}{profile_name}.{key} -> {value!r}")
        total += len(changed)

    if not dry_run:
        click.echo(f"Trimmed {total} value(s) across {len(results)} profile(s).")
