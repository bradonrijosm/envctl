"""CLI commands for searching environment variable profiles."""

from __future__ import annotations

import click

from envctl.search import SearchError, search_profiles


@click.group(name="search")
def cmd_search() -> None:
    """Search profiles by variable key or value."""


@cmd_search.command(name="run")
@click.option("-k", "--key", "key_pattern", default=None, help="Glob pattern for variable name.")
@click.option("-v", "--value", "value_pattern", default=None, help="Glob pattern for variable value.")
@click.option("-c", "--case-sensitive", is_flag=True, default=False, help="Enable case-sensitive matching.")
@click.option("--profile", "filter_profile", default=None, help="Restrict results to a specific profile.")
def search_run(
    key_pattern: str | None,
    value_pattern: str | None,
    case_sensitive: bool,
    filter_profile: str | None,
) -> None:
    """Search for variables matching the given patterns."""
    if not key_pattern and not value_pattern:
        raise click.UsageError("Provide at least --key or --value pattern.")

    try:
        matches = search_profiles(
            key_pattern=key_pattern,
            value_pattern=value_pattern,
            case_sensitive=case_sensitive,
        )
    except SearchError as exc:
        raise click.ClickException(str(exc)) from exc

    if filter_profile:
        matches = [m for m in matches if m.profile == filter_profile]

    if not matches:
        click.echo("No matches found.")
        return

    current_profile = None
    for match in matches:
        if match.profile != current_profile:
            current_profile = match.profile
            click.echo(f"\n[{current_profile}]")
        click.echo(f"  {match.key}={match.value}")
    click.echo()
