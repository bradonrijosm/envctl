"""CLI commands for profile locking."""

from __future__ import annotations

import click

from envctl.lock import LockError, list_locked, lock_profile, unlock_profile, is_locked


@click.group("lock")
def cmd_lock() -> None:
    """Lock or unlock profiles to prevent modification."""


@cmd_lock.command("add")
@click.argument("name")
def lock_add(name: str) -> None:
    """Lock profile NAME."""
    try:
        lock_profile(name)
        click.echo(f"Profile '{name}' is now locked.")
    except LockError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_lock.command("remove")
@click.argument("name")
def lock_remove(name: str) -> None:
    """Unlock profile NAME."""
    try:
        unlock_profile(name)
        click.echo(f"Profile '{name}' has been unlocked.")
    except LockError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_lock.command("status")
@click.argument("name")
def lock_status(name: str) -> None:
    """Show lock status of profile NAME."""
    state = "locked" if is_locked(name) else "unlocked"
    click.echo(f"Profile '{name}' is {state}.")


@cmd_lock.command("list")
def lock_list() -> None:
    """List all locked profiles."""
    locked = list_locked()
    if not locked:
        click.echo("No profiles are locked.")
    else:
        for name in locked:
            click.echo(name)
