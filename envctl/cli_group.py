"""CLI commands for group management."""
import click

from envctl.group import (
    GroupError,
    add_profile_to_group,
    create_group,
    delete_group,
    get_group_members,
    list_groups,
    remove_profile_from_group,
)


@click.group("group")
def cmd_group():
    """Manage profile groups."""


@cmd_group.command("create")
@click.argument("name")
def group_create(name: str):
    """Create a new empty group."""
    try:
        create_group(name)
        click.echo(f"Group '{name}' created.")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_group.command("delete")
@click.argument("name")
def group_delete(name: str):
    """Delete a group."""
    try:
        delete_group(name)
        click.echo(f"Group '{name}' deleted.")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_group.command("add")
@click.argument("group")
@click.argument("profile")
def group_add(group: str, profile: str):
    """Add PROFILE to GROUP."""
    try:
        add_profile_to_group(group, profile)
        click.echo(f"Profile '{profile}' added to group '{group}'.")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_group.command("remove")
@click.argument("group")
@click.argument("profile")
def group_remove(group: str, profile: str):
    """Remove PROFILE from GROUP."""
    try:
        remove_profile_from_group(group, profile)
        click.echo(f"Profile '{profile}' removed from group '{group}'.")
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_group.command("list")
def group_list():
    """List all groups and their members."""
    groups = list_groups()
    if not groups:
        click.echo("No groups defined.")
        return
    for name, members in sorted(groups.items()):
        member_str = ", ".join(members) if members else "(empty)"
        click.echo(f"{name}: {member_str}")


@cmd_group.command("show")
@click.argument("name")
def group_show(name: str):
    """Show members of a group."""
    try:
        members = get_group_members(name)
        if not members:
            click.echo(f"Group '{name}' is empty.")
        else:
            for m in members:
                click.echo(m)
    except GroupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
