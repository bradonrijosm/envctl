"""CLI commands for the envctl audit log."""

from __future__ import annotations

import time
from datetime import datetime

import click

from envctl.audit import AuditError, clear_audit_log, get_audit_log


@click.group("audit")
def cmd_audit() -> None:
    """View and manage the audit log of profile changes."""


@cmd_audit.command("log")
@click.option("--profile", "-p", default=None, help="Filter entries by profile name.")
@click.option("--limit", "-n", default=20, show_default=True, help="Max entries to show.")
def audit_log(profile: str | None, limit: int) -> None:
    """Display recent audit log entries."""
    try:
        entries = get_audit_log(profile=profile, limit=limit)
    except AuditError as exc:
        raise click.ClickException(str(exc)) from exc

    if not entries:
        click.echo("No audit entries found.")
        return

    for entry in entries:
        ts = datetime.fromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        action = entry["action"].upper().ljust(8)
        prof = entry["profile"]
        detail = f"  ({entry['detail']})" if "detail" in entry else ""
        click.echo(f"[{ts}] {action} {prof}{detail}")


@cmd_audit.command("clear")
@click.confirmation_option(prompt="Clear the entire audit log?")
def audit_clear() -> None:
    """Delete all audit log entries."""
    try:
        count = clear_audit_log()
    except AuditError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Cleared {count} audit log entr{'y' if count == 1 else 'ies'}.")  
