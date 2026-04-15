"""CLI commands for archive / restore of profile stores."""
from __future__ import annotations

from pathlib import Path

import click

from envctl.archive import ArchiveError, create_archive, inspect_archive, restore_archive


@click.group(name="archive")
def cmd_archive() -> None:
    """Archive and restore profile stores."""


@cmd_archive.command("create")
@click.argument("dest")
@click.option("--label", default="", help="Optional human-readable label.")
def archive_create(dest: str, label: str) -> None:
    """Create a zip archive of all current profiles at DEST."""
    try:
        path = create_archive(Path(dest), label=label)
        click.echo(f"Archive created: {path}")
    except ArchiveError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_archive.command("restore")
@click.argument("src")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing profiles with archived values.",
)
def archive_restore(src: str, overwrite: bool) -> None:
    """Restore profiles from a zip archive at SRC."""
    try:
        manifest = restore_archive(Path(src), overwrite=overwrite)
        label = manifest.get("label") or "(no label)"
        created = manifest.get("created_at", "unknown")
        click.echo(f"Restored archive — label: {label}, created: {created}")
    except ArchiveError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_archive.command("inspect")
@click.argument("src")
def archive_inspect(src: str) -> None:
    """Show contents of a zip archive without restoring."""
    try:
        info = inspect_archive(Path(src))
        m = info["manifest"]
        click.echo(f"Label   : {m.get('label') or '(none)'}")
        click.echo(f"Created : {m.get('created_at', 'unknown')}")
        click.echo(f"Profiles: {m.get('profile_count', len(info['profiles']))}")
        for name in info["profiles"]:
            click.echo(f"  - {name}")
    except ArchiveError as exc:
        raise click.ClickException(str(exc)) from exc
