"""CLI commands for snapshot management."""

from __future__ import annotations

import click

from envctl.snapshot import (
    create_snapshot,
    restore_snapshot,
    delete_snapshot,
    list_snapshots,
    SnapshotError,
)


@click.group("snapshot")
def cmd_snapshot() -> None:
    """Save and restore full environment profile snapshots."""


@cmd_snapshot.command("create")
@click.argument("name")
def snapshot_create(name: str) -> None:
    """Create a snapshot of all current profiles."""
    try:
        snap = create_snapshot(name)
        click.echo(f"Snapshot '{name}' created at {snap['created_at']}.")
    except SnapshotError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_snapshot.command("restore")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def snapshot_restore(name: str, yes: bool) -> None:
    """Restore profiles from a snapshot, overwriting current state."""
    if not yes:
        click.confirm(
            f"Restore snapshot '{name}'? This will overwrite all current profiles.",
            abort=True,
        )
    try:
        restore_snapshot(name)
        click.echo(f"Profiles restored from snapshot '{name}'.")
    except SnapshotError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_snapshot.command("delete")
@click.argument("name")
def snapshot_delete(name: str) -> None:
    """Delete a snapshot by name."""
    try:
        delete_snapshot(name)
        click.echo(f"Snapshot '{name}' deleted.")
    except SnapshotError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_snapshot.command("list")
def snapshot_list() -> None:
    """List all available snapshots."""
    snaps = list_snapshots()
    if not snaps:
        click.echo("No snapshots found.")
        return
    for snap in snaps:
        profile_count = len(snap["profiles"])
        click.echo(
            f"  {snap['name']:<24} {snap['created_at']}  ({profile_count} profile(s))"
        )
