"""CLI commands for managing per-key protection rules."""

from __future__ import annotations

import click

from envctl.env_protect import (
    ProtectError,
    protect_key,
    unprotect_key,
    list_protected,
    is_protected,
)


@click.group("protect")
def cmd_protect() -> None:
    """Manage protected (read-only) keys within a profile."""


@cmd_protect.command("add")
@click.argument("profile")
@click.argument("key")
def protect_add(profile: str, key: str) -> None:
    """Protect KEY in PROFILE so it cannot be overwritten or deleted."""
    try:
        protect_key(profile, key)
        click.echo(f"Key '{key}' is now protected in profile '{profile}'.")
    except ProtectError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_protect.command("remove")
@click.argument("profile")
@click.argument("key")
def protect_remove(profile: str, key: str) -> None:
    """Remove protection from KEY in PROFILE."""
    try:
        unprotect_key(profile, key)
        click.echo(f"Key '{key}' is no longer protected in profile '{profile}'.")
    except ProtectError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_protect.command("list")
@click.argument("profile")
def protect_list(profile: str) -> None:
    """List all protected keys in PROFILE."""
    keys = list_protected(profile)
    if not keys:
        click.echo(f"No protected keys in profile '{profile}'.")
    else:
        for k in keys:
            click.echo(k)


@cmd_protect.command("status")
@click.argument("profile")
@click.argument("key")
def protect_status(profile: str, key: str) -> None:
    """Show whether KEY in PROFILE is protected."""
    if is_protected(profile, key):
        click.echo(f"Key '{key}' in profile '{profile}' is PROTECTED.")
    else:
        click.echo(f"Key '{key}' in profile '{profile}' is not protected.")
