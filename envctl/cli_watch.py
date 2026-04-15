"""CLI commands for the watch feature."""

from __future__ import annotations

import click

from envctl.watch import WatchError, watch_profile


def _default_on_change(profile: str, old: dict, new: dict) -> None:
    added = set(new) - set(old)
    removed = set(old) - set(new)
    changed = {k for k in set(old) & set(new) if old[k] != new[k]}

    click.echo(f"[watch] Profile '{profile}' changed:")
    for k in sorted(added):
        click.echo(f"  + {k}={new[k]}")
    for k in sorted(removed):
        click.echo(f"  - {k}")
    for k in sorted(changed):
        click.echo(f"  ~ {k}: {old[k]!r} -> {new[k]!r}")
    click.echo("  # Re-source your environment to apply changes.")


@click.group("watch")
def cmd_watch() -> None:
    """Watch a profile for live changes."""


@cmd_watch.command("start")
@click.argument("profile")
@click.option(
    "--interval",
    default=2.0,
    show_default=True,
    help="Polling interval in seconds.",
)
def watch_start(profile: str, interval: float) -> None:
    """Watch PROFILE and print a diff whenever it changes."""
    click.echo(f"Watching profile '{profile}' (interval={interval}s). Press Ctrl+C to stop.")
    try:
        watch_profile(profile, _default_on_change, interval=interval)
    except WatchError as exc:
        raise click.ClickException(str(exc)) from exc
