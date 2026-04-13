"""CLI entry point for envctl using Click."""

import sys

import click

from envctl.profiles import (
    ProfileError,
    create_profile,
    export_shell,
    get_profile,
    list_profiles,
    remove_profile,
    update_profile,
)


@click.group()
def cli():
    """envctl — manage and switch named environment variable profiles."""


@cli.command("create")
@click.argument("name")
@click.option("-e", "--env", multiple=True, metavar="KEY=VALUE", help="Environment variable.")
def cmd_create(name, env):
    """Create a new profile NAME with given variables."""
    variables = _parse_env_pairs(env)
    try:
        create_profile(name, variables)
        click.echo(f"Profile '{name}' created with {len(variables)} variable(s).")
    except ProfileError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("update")
@click.argument("name")
@click.option("-e", "--env", multiple=True, metavar="KEY=VALUE", help="Environment variable.")
@click.option("--merge", is_flag=True, default=False, help="Merge with existing variables.")
def cmd_update(name, env, merge):
    """Update profile NAME with new variables."""
    variables = _parse_env_pairs(env)
    try:
        update_profile(name, variables, merge=merge)
        click.echo(f"Profile '{name}' updated.")
    except ProfileError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("delete")
@click.argument("name")
def cmd_delete(name):
    """Delete profile NAME."""
    try:
        remove_profile(name)
        click.echo(f"Profile '{name}' deleted.")
    except ProfileError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("list")
def cmd_list():
    """List all stored profiles."""
    names = list_profiles()
    if not names:
        click.echo("No profiles found.")
    for name in names:
        click.echo(name)


@cli.command("show")
@click.argument("name")
def cmd_show(name):
    """Show variables in profile NAME."""
    try:
        variables = get_profile(name)
        for key, value in sorted(variables.items()):
            click.echo(f"{key}={value}")
    except ProfileError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("export")
@click.argument("name")
def cmd_export(name):
    """Print shell export statements for profile NAME."""
    try:
        click.echo(export_shell(name))
    except ProfileError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


def _parse_env_pairs(pairs):
    result = {}
    for pair in pairs:
        if "=" not in pair:
            click.echo(f"Invalid format '{pair}'. Expected KEY=VALUE.", err=True)
            sys.exit(1)
        key, _, value = pair.partition("=")
        result[key.strip()] = value.strip()
    return result
