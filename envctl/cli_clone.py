"""CLI commands for profile cloning."""

from __future__ import annotations

import click

from envctl.clone import CloneError, clone_profile, clone_with_prefix


@click.group(name="clone")
def cmd_clone() -> None:
    """Clone a profile into a new profile."""


@cmd_clone.command(name="copy")
@click.argument("source")
@click.argument("dest")
@click.option(
    "-s",
    "--set",
    "overrides",
    metavar="KEY=VALUE",
    multiple=True,
    help="Override or add a variable in the cloned profile.",
)
def clone_copy(source: str, dest: str, overrides: tuple) -> None:
    """Clone SOURCE profile to DEST, with optional variable overrides."""
    parsed: dict = {}
    for item in overrides:
        if "=" not in item:
            raise click.BadParameter(
                f"Expected KEY=VALUE, got '{item}'", param_hint="--set"
            )
        k, v = item.split("=", 1)
        parsed[k] = v

    try:
        vars_ = clone_profile(source, dest, overrides=parsed or None)
    except CloneError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Cloned '{source}' → '{dest}' ({len(vars_)} variables).")


@cmd_clone.command(name="prefix")
@click.argument("source")
@click.argument("dest")
@click.argument("prefix")
def clone_prefix(source: str, dest: str, prefix: str) -> None:
    """Clone SOURCE to DEST, prefixing every variable name with PREFIX."""
    try:
        vars_ = clone_with_prefix(source, dest, prefix)
    except CloneError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(
        f"Cloned '{source}' → '{dest}' with prefix '{prefix}' ({len(vars_)} variables)."
    )
