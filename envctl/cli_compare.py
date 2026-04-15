"""CLI command for comparing two environment profiles."""

import click

from envctl.compare import CompareError, compare_profiles, format_compare


@click.group("compare")
def cmd_compare():
    """Compare two environment profiles."""


@cmd_compare.command("show")
@click.argument("profile_a")
@click.argument("profile_b")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON.")
def compare_show(profile_a: str, profile_b: str, as_json: bool):
    """Show differences between PROFILE_A and PROFILE_B."""
    try:
        result = compare_profiles(profile_a, profile_b)
    except CompareError as exc:
        raise click.ClickException(str(exc))

    if as_json:
        import json

        payload = {
            "profile_a": result.profile_a,
            "profile_b": result.profile_b,
            "identical": result.are_identical,
            "similarity_pct": result.similarity_pct,
            "only_in_a": result.only_in_a,
            "only_in_b": result.only_in_b,
            "in_both_same": result.in_both_same,
            "in_both_different": {
                k: {"a": va, "b": vb}
                for k, (va, vb) in result.in_both_different.items()
            },
        }
        click.echo(json.dumps(payload, indent=2))
    else:
        for line in format_compare(result):
            click.echo(line)


@cmd_compare.command("summary")
@click.argument("profile_a")
@click.argument("profile_b")
def compare_summary(profile_a: str, profile_b: str):
    """Print a one-line similarity summary for PROFILE_A vs PROFILE_B."""
    try:
        result = compare_profiles(profile_a, profile_b)
    except CompareError as exc:
        raise click.ClickException(str(exc))

    click.echo(
        f"'{profile_a}' vs '{profile_b}': "
        f"{result.similarity_pct}% similar  "
        f"(same={len(result.in_both_same)}, "
        f"changed={len(result.in_both_different)}, "
        f"only_a={len(result.only_in_a)}, "
        f"only_b={len(result.only_in_b)})"
    )
