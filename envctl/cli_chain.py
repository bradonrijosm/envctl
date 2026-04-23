"""cli_chain.py – CLI commands for managing profile chains."""
from __future__ import annotations

import click

from envctl.env_chain import (
    ChainError,
    create_chain,
    delete_chain,
    get_chain,
    list_chains,
    resolve_chain,
)


@click.group(name="chain")
def cmd_chain():
    """Manage ordered profile chains."""


@cmd_chain.command("create")
@click.argument("name")
@click.argument("profiles", nargs=-1, required=True)
def chain_create(name: str, profiles):
    """Create a named chain from an ordered list of PROFILES."""
    try:
        create_chain(name, list(profiles))
        click.echo(f"Chain '{name}' created with profiles: {', '.join(profiles)}")
    except ChainError as exc:
        raise click.ClickException(str(exc))


@cmd_chain.command("delete")
@click.argument("name")
def chain_delete(name: str):
    """Delete a named chain."""
    try:
        delete_chain(name)
        click.echo(f"Chain '{name}' deleted.")
    except ChainError as exc:
        raise click.ClickException(str(exc))


@cmd_chain.command("show")
@click.argument("name")
def chain_show(name: str):
    """Show the profiles in a chain."""
    profiles = get_chain(name)
    if profiles is None:
        raise click.ClickException(f"Chain '{name}' does not exist.")
    click.echo(f"Chain '{name}': {' -> '.join(profiles)}")


@cmd_chain.command("list")
def chain_list():
    """List all defined chains."""
    chains = list_chains()
    if not chains:
        click.echo("No chains defined.")
        return
    for cname, profiles in sorted(chains.items()):
        click.echo(f"  {cname}: {' -> '.join(profiles)}")


@cmd_chain.command("resolve")
@click.argument("name")
def chain_resolve(name: str):
    """Print the merged variables produced by resolving a chain."""
    try:
        merged = resolve_chain(name)
    except ChainError as exc:
        raise click.ClickException(str(exc))
    if not merged:
        click.echo("(empty)")
        return
    for key, value in sorted(merged.items()):
        click.echo(f"{key}={value}")
