"""CLI commands for freeze / unfreeze of profile variables."""

from __future__ import annotations

import click

from envctl.env_freeze import (
    FreezeError,
    freeze_profile,
    unfreeze_profile,
    is_frozen,
    list_frozen,
)


@click.group(name="freeze")
def cmd_freeze() -> None:
    """Freeze or unfreeze profile variables to prevent accidental modification."""


@cmd_freeze.command(name="add")
@click.argument("profile")
@click.argument("keys", nargs=-1)
def freeze_add(profile: str, keys: tuple[str, ...]) -> None:
    """Freeze PROFILE entirely, or only specific KEYS."""
    try:
        freeze_profile(profile, list(keys) if keys else None)
        scope = ", ".join(keys) if keys else "all keys"
        click.echo(f"Frozen '{profile}' ({scope}).")
    except FreezeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_freeze.command(name="remove")
@click.argument("profile")
@click.argument("keys", nargs=-1)
def freeze_remove(profile: str, keys: tuple[str, ...]) -> None:
    """Unfreeze PROFILE entirely, or only specific KEYS."""
    try:
        unfreeze_profile(profile, list(keys) if keys else None)
        scope = ", ".join(keys) if keys else "all keys"
        click.echo(f"Unfrozen '{profile}' ({scope}).")
    except FreezeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_freeze.command(name="status")
@click.argument("profile")
@click.argument("key", required=False, default=None)
def freeze_status(profile: str, key: str | None) -> None:
    """Check whether PROFILE (or a specific KEY) is frozen."""
    frozen = is_frozen(profile, key)
    target = f"'{key}' in '{profile}'" if key else f"'{profile}'"
    click.echo(f"{target} is {'frozen' if frozen else 'not frozen'}.")


@cmd_freeze.command(name="list")
def freeze_list() -> None:
    """List all frozen profiles and their frozen keys."""
    data = list_frozen()
    if not data:
        click.echo("No frozen profiles.")
        return
    for profile, keys in sorted(data.items()):
        scope = "(all)" if keys == ["*"] else ", ".join(keys)
        click.echo(f"  {profile}: {scope}")
