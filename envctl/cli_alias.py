"""CLI commands for profile alias management."""

from __future__ import annotations

import click

from envctl.alias import (
    AliasError,
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    rename_alias,
)


@click.group("alias")
def cmd_alias() -> None:
    """Manage profile aliases."""


@cmd_alias.command("add")
@click.argument("alias")
@click.argument("profile")
def alias_add(alias: str, profile: str) -> None:
    """Create ALIAS pointing to PROFILE."""
    try:
        add_alias(alias, profile)
        click.echo(f"Alias '{alias}' -> '{profile}' created.")
    except AliasError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_alias.command("remove")
@click.argument("alias")
def alias_remove(alias: str) -> None:
    """Remove ALIAS."""
    try:
        remove_alias(alias)
        click.echo(f"Alias '{alias}' removed.")
    except AliasError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_alias.command("resolve")
@click.argument("alias")
def alias_resolve(alias: str) -> None:
    """Show the profile that ALIAS points to."""
    target = resolve_alias(alias)
    if target is None:
        raise click.ClickException(f"Alias '{alias}' does not exist.")
    click.echo(target)


@cmd_alias.command("list")
def alias_list() -> None:
    """List all aliases."""
    aliases = list_aliases()
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, profile in sorted(aliases.items()):
        click.echo(f"{alias} -> {profile}")


@cmd_alias.command("rename")
@click.argument("alias")
@click.argument("new_alias")
def alias_rename(alias: str, new_alias: str) -> None:
    """Rename ALIAS to NEW_ALIAS."""
    try:
        rename_alias(alias, new_alias)
        click.echo(f"Alias '{alias}' renamed to '{new_alias}'.")
    except AliasError as exc:
        raise click.ClickException(str(exc)) from exc
