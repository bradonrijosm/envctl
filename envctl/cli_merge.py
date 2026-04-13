"""CLI command for merging profiles."""

import click
from envctl.merge import merge_profiles, MergeError


@click.command("merge")
@click.argument("source")
@click.argument("target")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing keys in TARGET with values from SOURCE.",
)
def cmd_merge(source: str, target: str, overwrite: bool) -> None:
    """Merge variables from SOURCE profile into TARGET profile.

    By default, keys already present in TARGET are not overwritten.
    Pass --overwrite to let SOURCE values take precedence.
    """
    try:
        merged = merge_profiles(source, target, overwrite=overwrite)
    except MergeError as exc:
        raise click.ClickException(str(exc)) from exc

    mode = "overwrite" if overwrite else "non-destructive"
    click.echo(
        f"Merged '{source}' → '{target}' ({mode}). "
        f"{len(merged)} variable(s) now in '{target}'."
    )
