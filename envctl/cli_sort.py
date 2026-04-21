"""CLI commands for sorting profile variables."""
import click
from envctl.env_sort import sort_profile, SortError


@click.group(name="sort")
def cmd_sort() -> None:
    """Sort environment variables within a profile."""


@cmd_sort.command(name="run")
@click.argument("profile")
@click.option(
    "--by",
    type=click.Choice(["key", "value"]),
    default="key",
    show_default=True,
    help="Field to sort by.",
)
@click.option("--reverse", is_flag=True, default=False, help="Sort in descending order.")
@click.option("--quiet", is_flag=True, default=False, help="Suppress output of sorted variables.")
def sort_run(profile: str, by: str, reverse: bool, quiet: bool) -> None:
    """Sort variables in PROFILE and persist the result."""
    try:
        sorted_vars = sort_profile(profile, by=by, reverse=reverse)  # type: ignore[arg-type]
    except SortError as exc:
        raise click.ClickException(str(exc)) from exc

    direction = "descending" if reverse else "ascending"
    click.echo(f"Sorted '{profile}' by {by} ({direction}): {len(sorted_vars)} variable(s).")
    if not quiet:
        for k, v in sorted_vars.items():
            click.echo(f"  {k}={v}")
