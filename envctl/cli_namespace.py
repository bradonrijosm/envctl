"""CLI commands for the env-namespace feature."""

from __future__ import annotations

import click

from envctl.env_namespace import (
    NamespaceError,
    delete_namespace,
    get_namespace,
    list_namespaces,
    set_namespace,
)


@click.group("namespace")
def cmd_namespace() -> None:
    """Manage variable namespaces within a profile."""


@cmd_namespace.command("list")
@click.argument("profile")
def ns_list(profile: str) -> None:
    """List all namespaces present in PROFILE."""
    try:
        namespaces = list_namespaces(profile)
    except NamespaceError as exc:
        raise click.ClickException(str(exc)) from exc
    if not namespaces:
        click.echo(f"No namespaces found in '{profile}'.")
        return
    for ns in namespaces:
        click.echo(ns)


@cmd_namespace.command("get")
@click.argument("profile")
@click.argument("namespace")
def ns_get(profile: str, namespace: str) -> None:
    """Show variables in NAMESPACE within PROFILE."""
    try:
        variables = get_namespace(profile, namespace)
    except NamespaceError as exc:
        raise click.ClickException(str(exc)) from exc
    if not variables:
        click.echo(f"No variables found under namespace '{namespace}'.")
        return
    for key, value in sorted(variables.items()):
        click.echo(f"{key}={value}")


@cmd_namespace.command("set")
@click.argument("profile")
@click.argument("namespace")
@click.argument("pairs", nargs=-1, required=True, metavar="KEY=VALUE...")
@click.option("--no-overwrite", is_flag=True, default=False)
def ns_set(profile: str, namespace: str, pairs: tuple, no_overwrite: bool) -> None:
    """Write KEY=VALUE pairs under NAMESPACE in PROFILE."""
    variables: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(f"Expected KEY=VALUE, got '{pair}'.")
        k, _, v = pair.partition("=")
        variables[k] = v
    try:
        updated = set_namespace(profile, namespace, variables, overwrite=not no_overwrite)
    except NamespaceError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Set {len(updated)} variable(s) under namespace '{namespace}'.")


@cmd_namespace.command("delete")
@click.argument("profile")
@click.argument("namespace")
def ns_delete(profile: str, namespace: str) -> None:
    """Remove all variables under NAMESPACE from PROFILE."""
    try:
        removed = delete_namespace(profile, namespace)
    except NamespaceError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Removed {len(removed)} variable(s) from namespace '{namespace}'.")
