"""CLI commands for profile inheritance."""

from __future__ import annotations

import click

from envctl.inherit import InheritError, inherit_profile, rebase_profile


@click.group("inherit")
def cmd_inherit() -> None:
    """Derive and rebase environment profiles."""


@cmd_inherit.command("create")
@click.argument("base")
@click.argument("derived")
@click.option(
    "-s",
    "--set",
    "pairs",
    multiple=True,
    metavar="KEY=VALUE",
    help="Override variable in the derived profile (repeatable).",
)
def inherit_create(base: str, derived: str, pairs: tuple) -> None:
    """Create DERIVED profile inheriting from BASE with optional overrides."""
    overrides: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(
                f"Expected KEY=VALUE, got '{pair}'", param_hint="--set"
            )
        k, _, v = pair.partition("=")
        overrides[k.strip()] = v

    try:
        merged = inherit_profile(base, derived, overrides)
    except InheritError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(
        f"Created '{derived}' from '{base}' with {len(merged)} variable(s)."
    )


@cmd_inherit.command("rebase")
@click.argument("profile")
@click.argument("new_base")
def inherit_rebase(profile: str, new_base: str) -> None:
    """Rebase PROFILE on top of NEW_BASE, preserving its own overrides."""
    try:
        merged = rebase_profile(profile, new_base)
    except InheritError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(
        f"Rebased '{profile}' onto '{new_base}'; now has {len(merged)} variable(s)."
    )
