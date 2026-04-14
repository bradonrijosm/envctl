"""CLI commands for managing profile tags."""

import click
from envctl.tags import TagError, add_tag, remove_tag, list_tags, get_profiles_by_tag


@click.group(name="tag")
def cmd_tag():
    """Manage tags on environment profiles."""
    pass


@cmd_tag.command(name="add")
@click.argument("profile")
@click.argument("tag")
def tag_add(profile: str, tag: str):
    """Add a TAG to a PROFILE.

    Example:
        envctl tag add production deploy
    """
    try:
        add_tag(profile, tag)
        click.echo(f"Tag '{tag}' added to profile '{profile}'.")
    except TagError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_tag.command(name="remove")
@click.argument("profile")
@click.argument("tag")
def tag_remove(profile: str, tag: str):
    """Remove a TAG from a PROFILE.

    Example:
        envctl tag remove production deploy
    """
    try:
        remove_tag(profile, tag)
        click.echo(f"Tag '{tag}' removed from profile '{profile}'.")
    except TagError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_tag.command(name="list")
@click.argument("profile")
def tag_list(profile: str):
    """List all tags on a PROFILE.

    Example:
        envctl tag list production
    """
    try:
        tags = list_tags(profile)
        if not tags:
            click.echo(f"No tags on profile '{profile}'.")
        else:
            click.echo(f"Tags for '{profile}':")
            for t in sorted(tags):
                click.echo(f"  - {t}")
    except TagError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_tag.command(name="find")
@click.argument("tag")
def tag_find(tag: str):
    """Find all profiles that have a given TAG.

    Example:
        envctl tag find deploy
    """
    try:
        profiles = get_profiles_by_tag(tag)
        if not profiles:
            click.echo(f"No profiles found with tag '{tag}'.")
        else:
            click.echo(f"Profiles tagged '{tag}':")
            for p in sorted(profiles):
                click.echo(f"  - {p}")
    except TagError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
