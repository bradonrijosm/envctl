"""CLI commands for filtering profile variables."""

from __future__ import annotations

import click

from envctl.env_filter import FilterError, apply_filter, filter_profile


@click.group(name="filter")
def cmd_filter() -> None:
    """Filter profile variables by key or value pattern."""


@cmd_filter.command(name="show")
@click.argument("profile")
@click.option("-k", "--key", "key_pattern", default=None, help="Glob pattern for key names.")
@click.option("-v", "--value", "value_pattern", default=None, help="Glob pattern for values.")
@click.option("--invert", is_flag=True, default=False, help="Return non-matching variables.")
@click.option("--case-sensitive", is_flag=True, default=False, help="Enable case-sensitive matching.")
def filter_show(
    profile: str,
    key_pattern: str | None,
    value_pattern: str | None,
    invert: bool,
    case_sensitive: bool,
) -> None:
    """Preview filtered variables without modifying the profile."""
    try:
        result = filter_profile(
            profile,
            key_pattern=key_pattern,
            value_pattern=value_pattern,
            invert=invert,
            case_sensitive=case_sensitive,
        )
    except FilterError as exc:
        raise click.ClickException(str(exc)) from exc

    if not result:
        click.echo("No variables matched.")
        return
    for key, value in sorted(result.items()):
        click.echo(f"{key}={value}")


@cmd_filter.command(name="apply")
@click.argument("profile")
@click.option("-k", "--key", "key_pattern", default=None, help="Glob pattern for key names.")
@click.option("-v", "--value", "value_pattern", default=None, help="Glob pattern for values.")
@click.option("--invert", is_flag=True, default=False, help="Keep non-matching variables.")
@click.option("--case-sensitive", is_flag=True, default=False, help="Enable case-sensitive matching.")
def filter_apply(
    profile: str,
    key_pattern: str | None,
    value_pattern: str | None,
    invert: bool,
    case_sensitive: bool,
) -> None:
    """Filter profile variables in-place and persist the result."""
    try:
        kept = apply_filter(
            profile,
            key_pattern=key_pattern,
            value_pattern=value_pattern,
            invert=invert,
            case_sensitive=case_sensitive,
        )
    except FilterError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Profile '{profile}' updated — {len(kept)} variable(s) retained.")
