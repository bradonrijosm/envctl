"""CLI command for promoting variables between profiles."""

import click
from envctl.promote import promote_profile, PromoteError


@click.group("promote")
def cmd_promote():
    """Promote variables from one profile into another."""


@cmd_promote.command("run")
@click.argument("source")
@click.argument("target")
@click.option(
    "--key",
    "-k",
    "keys",
    multiple=True,
    help="Specific variable(s) to promote. Repeatable. Defaults to all.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing keys in the target profile.",
)
def promote_run(source: str, target: str, keys: tuple, overwrite: bool):
    """Promote variables from SOURCE into TARGET.

    By default only keys that do not yet exist in TARGET are written.
    Use --overwrite to replace existing values.
    """
    try:
        promoted = promote_profile(
            source,
            target,
            keys=list(keys) if keys else None,
            overwrite=overwrite,
        )
    except PromoteError as exc:
        raise click.ClickException(str(exc)) from exc

    if not promoted:
        click.echo("Nothing promoted (all keys already exist; use --overwrite to force).")
        return

    click.echo(f"Promoted {len(promoted)} variable(s) from '{source}' → '{target}':")
    for k, v in sorted(promoted.items()):
        click.echo(f"  {k}={v}")
