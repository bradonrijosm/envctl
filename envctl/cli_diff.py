"""CLI commands for diffing environment profiles."""

import click
from envctl.storage import load_profiles
from envctl.diff import diff_profiles, format_diff
from envctl.profiles import ProfileError


@click.command("diff")
@click.argument("profile_a")
@click.argument("profile_b")
@click.option("--unchanged", is_flag=True, default=False, help="Also show unchanged variables.")
@click.option("--no-color", is_flag=True, default=False, help="Disable colored output.")
def cmd_diff(profile_a: str, profile_b: str, unchanged: bool, no_color: bool) -> None:
    """Show differences between two named profiles.

    PROFILE_A is the base profile; PROFILE_B is the target profile.
    """
    profiles = load_profiles()

    if profile_a not in profiles:
        raise click.ClickException(f"Profile '{profile_a}' not found.")
    if profile_b not in profiles:
        raise click.ClickException(f"Profile '{profile_b}' not found.")

    vars_a: dict = profiles[profile_a].get("variables", {})
    vars_b: dict = profiles[profile_b].get("variables", {})

    entries = diff_profiles(vars_a, vars_b, show_unchanged=unchanged)

    if not entries:
        click.echo(f"Profiles '{profile_a}' and '{profile_b}' are identical.")
        return

    header = f"--- {profile_a}\n+++ {profile_b}"
    click.echo(header)
    click.echo(format_diff(entries, color=not no_color))
    click.echo()
    added = sum(1 for e in entries if e.status == "added")
    removed = sum(1 for e in entries if e.status == "removed")
    changed = sum(1 for e in entries if e.status == "changed")
    click.echo(f"Summary: +{added} added, -{removed} removed, ~{changed} changed")
