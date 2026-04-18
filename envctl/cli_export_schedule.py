"""CLI commands for scheduled profile export."""
from __future__ import annotations

import click
from pathlib import Path

from envctl.env_export_schedule import ScheduleConfig, ScheduleError, run_schedule


@click.group(name="schedule")
def cmd_schedule():
    """Scheduled export of a profile to a file."""


@cmd_schedule.command(name="run")
@click.argument("profile")
@click.argument("output", type=click.Path())
@click.option("--fmt", default="dotenv", show_default=True,
              type=click.Choice(["bash", "fish", "dotenv"]),
              help="Export format.")
@click.option("--interval", default=60, show_default=True, type=int,
              help="Seconds between exports.")
@click.option("--runs", default=None, type=int,
              help="Maximum number of export runs (omit for infinite).")
def schedule_run(profile: str, output: str, fmt: str, interval: int, runs):
    """Continuously export PROFILE to OUTPUT file every INTERVAL seconds."""
    def on_write(p: Path):
        click.echo(f"Exported '{profile}' -> {p}")

    config = ScheduleConfig(
        profile=profile,
        output_path=Path(output),
        fmt=fmt,
        interval=interval,
        max_runs=runs,
        on_write=on_write,
    )
    try:
        run_schedule(config)
    except ScheduleError as exc:
        raise click.ClickException(str(exc))
    except KeyboardInterrupt:
        click.echo("Schedule stopped.")
