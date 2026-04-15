"""CLI commands for rolling back a profile to a previous state."""

from __future__ import annotations

import click

from envctl.rollback import RollbackError, rollback_to_snapshot, rollback_to_history


@click.group(name="rollback")
def cmd_rollback():
    """Revert a profile to a previous snapshot or history entry."""


@cmd_rollback.command(name="snapshot")
@click.argument("profile")
@click.argument("snapshot")
def rollback_snapshot(profile: str, snapshot: str):
    """Restore PROFILE variables from a named SNAPSHOT."""
    try:
        restored = rollback_to_snapshot(profile, snapshot)
        click.echo(
            f"Profile '{profile}' rolled back to snapshot '{snapshot}' "
            f"({len(restored)} variable(s))."
        )
    except RollbackError as exc:
        raise click.ClickException(str(exc)) from exc


@cmd_rollback.command(name="history")
@click.argument("profile")
@click.option(
    "--steps",
    "-n",
    default=1,
    show_default=True,
    type=click.IntRange(min=1),
    help="Number of history entries to roll back.",
)
def rollback_history(profile: str, steps: int):
    """Revert PROFILE to a state recorded N history entries ago."""
    try:
        restored = rollback_to_history(profile, steps)
        click.echo(
            f"Profile '{profile}' rolled back {steps} step(s) via history "
            f"({len(restored)} variable(s))."
        )
    except RollbackError as exc:
        raise click.ClickException(str(exc)) from exc
