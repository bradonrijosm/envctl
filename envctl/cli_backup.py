"""CLI commands for profile backup and restore."""

from __future__ import annotations

import click

from envctl.env_backup import BackupError, backup_profile, restore_profile, list_backups


@click.group(name="backup")
def cmd_backup() -> None:
    """Backup and restore profile snapshots to/from JSON files."""


@cmd_backup.command(name="create")
@click.argument("profile")
@click.option("-d", "--dest", default="./envctl-backups", show_default=True,
              help="Directory to write the backup file.")
@click.option("-l", "--label", default=None, help="Optional label embedded in the filename.")
def backup_create(profile: str, dest: str, label: str | None) -> None:
    """Backup PROFILE to a JSON file."""
    try:
        path = backup_profile(profile, dest, label=label)
        click.echo(f"Backup written: {path}")
    except BackupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_backup.command(name="restore")
@click.argument("backup_file")
@click.option("--overwrite", is_flag=True, default=False,
              help="Overwrite the profile if it already exists.")
def backup_restore(backup_file: str, overwrite: bool) -> None:
    """Restore a profile from BACKUP_FILE."""
    try:
        name = restore_profile(backup_file, overwrite=overwrite)
        click.echo(f"Profile '{name}' restored from {backup_file}.")
    except BackupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_backup.command(name="list")
@click.option("-d", "--dest", default="./envctl-backups", show_default=True,
              help="Directory to search for backup files.")
def backup_list(dest: str) -> None:
    """List available backup files in DEST."""
    entries = list_backups(dest)
    if not entries:
        click.echo("No backup files found.")
        return
    for entry in entries:
        label = f" [{entry['label']}]" if entry["label"] else ""
        click.echo(f"{entry['exported_at']}  {entry['profile']}{label}  {entry['file']}")
