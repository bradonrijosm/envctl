"""CLI commands for scope management."""

from __future__ import annotations

import click

from envctl.env_scope import (
    ScopeError,
    bind_scope,
    list_scopes,
    resolve_scope,
    unbind_scope,
)


@click.group(name="scope")
def cmd_scope() -> None:
    """Manage profile scopes (project-directory bindings)."""


@cmd_scope.command(name="bind")
@click.argument("scope")
@click.argument("profile")
def scope_bind(scope: str, profile: str) -> None:
    """Bind SCOPE to PROFILE."""
    try:
        bind_scope(scope, profile)
        click.echo(f"Scope '{scope}' bound to profile '{profile}'.")
    except ScopeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_scope.command(name="unbind")
@click.argument("scope")
def scope_unbind(scope: str) -> None:
    """Remove the binding for SCOPE."""
    try:
        unbind_scope(scope)
        click.echo(f"Scope '{scope}' unbound.")
    except ScopeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_scope.command(name="resolve")
@click.argument("scope")
def scope_resolve(scope: str) -> None:
    """Print the profile bound to SCOPE."""
    profile = resolve_scope(scope)
    if profile is None:
        click.echo(f"Scope '{scope}' is not bound.", err=True)
        raise SystemExit(1)
    click.echo(profile)


@cmd_scope.command(name="list")
def scope_list() -> None:
    """List all scope bindings."""
    entries = list_scopes()
    if not entries:
        click.echo("No scopes defined.")
        return
    for entry in entries:
        click.echo(f"{entry['scope']:30s} -> {entry['profile']}")
