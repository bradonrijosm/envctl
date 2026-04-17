"""CLI commands for managing profile TTLs."""
import click

from envctl.ttl import TTLError, set_ttl, get_ttl, remove_ttl, is_expired, list_ttls


@click.group(name="ttl")
def cmd_ttl():
    """Manage time-to-live expiry for profiles."""


@cmd_ttl.command(name="set")
@click.argument("profile")
@click.argument("seconds", type=int)
def ttl_set(profile: str, seconds: int):
    """Set a TTL of SECONDS for PROFILE."""
    try:
        set_ttl(profile, seconds)
        click.echo(f"TTL set: '{profile}' expires in {seconds}s.")
    except TTLError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_ttl.command(name="get")
@click.argument("profile")
def ttl_get(profile: str):
    """Show TTL info for PROFILE."""
    import time
    expires_at = get_ttl(profile)
    if expires_at is None:
        click.echo(f"No TTL set for '{profile}'.")
        return
    remaining = max(0.0, expires_at - time.time())
    expired = is_expired(profile)
    status = "EXPIRED" if expired else f"{remaining:.1f}s remaining"
    click.echo(f"Profile '{profile}': {status}")


@cmd_ttl.command(name="remove")
@click.argument("profile")
def ttl_remove(profile: str):
    """Remove the TTL from PROFILE."""
    try:
        remove_ttl(profile)
        click.echo(f"TTL removed from '{profile}'.")
    except TTLError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cmd_ttl.command(name="list")
def ttl_list():
    """List all profiles with TTLs."""
    entries = list_ttls()
    if not entries:
        click.echo("No TTLs configured.")
        return
    for entry in entries:
        status = "EXPIRED" if entry["expired"] else f"{entry['remaining_seconds']:.1f}s remaining"
        click.echo(f"  {entry['profile']}: {status}")
