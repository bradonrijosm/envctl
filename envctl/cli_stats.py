"""CLI commands for profile statistics."""
import click
from envctl.env_stats import StatsError, all_stats, profile_stats, summary_report


@click.group(name="stats")
def cmd_stats():
    """Show statistics for environment profiles."""


@cmd_stats.command(name="show")
@click.argument("profile")
def stats_show(profile: str):
    """Show detailed statistics for a single PROFILE."""
    try:
        s = profile_stats(profile)
    except StatsError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Profile      : {s.name}")
    click.echo(f"Variables    : {s.var_count}")
    click.echo(f"Empty values : {s.empty_count}")
    click.echo(f"Avg key len  : {s.avg_key_length:.1f}")
    click.echo(f"Avg val len  : {s.avg_value_length:.1f}")


@cmd_stats.command(name="summary")
def stats_summary():
    """Print a summary table of all profiles."""
    try:
        stats_list = all_stats()
    except StatsError as exc:
        raise click.ClickException(str(exc))
    click.echo(summary_report(stats_list))
