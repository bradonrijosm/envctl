"""CLI commands for renaming and cloning profiles."""

from __future__ import annotations

import click

from envctl.rename import RenameError, clone_profile, rename_profile


@click.group("rename")
def cmd_rename() -> None:
    """Rename or clone environment profiles."""


@cmd_rename.command("mv")
@click.argument("old_name")
@click.argument("new_name")
def rename_mv(old_name: str, new_name: str) -> None:
    """Rename OLD_NAME to NEW_NAME."""
    try:
        rename_profile(old_name, new_name)
        click.echo(f"Renamed profile '{old_name}' → '{new_name}'.")
    except RenameError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_rename.command("clone")
@click.argument("source")
@click.argument("dest")
@click.option(
    "--include",
    "include_keys",
    multiple=True,
    metavar="KEY",
    help="Only copy these variable keys (repeatable).",
)
@click.option(
    "--exclude",
    "exclude_keys",
    multiple=True,
    metavar="KEY",
    help="Skip these variable keys when cloning (repeatable).",
)
def rename_clone(
    source: str,
    dest: str,
    include_keys: tuple[str, ...],
    exclude_keys: tuple[str, ...],
) -> None:
    """Clone SOURCE profile into a new DEST profile."""
    try:
        variables = clone_profile(
            source,
            dest,
            include_keys=list(include_keys) if include_keys else None,
            exclude_keys=list(exclude_keys) if exclude_keys else None,
        )
        click.echo(
            f"Cloned '{source}' → '{dest}' ({len(variables)} variable(s) copied)."
        )
    except RenameError as exc:
        raise click.ClickException(str(exc)) from exc
