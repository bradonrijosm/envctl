"""CLI command: envctl patch <source> <target> [--overwrite] [--dry-run]"""
import click
from envctl.env_diff_apply import apply_diff, PatchError


@click.group("patch")
def cmd_patch() -> None:
    """Apply a profile diff as a patch onto another profile."""


@cmd_patch.command("apply")
@click.argument("source")
@click.argument("target")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite changed keys.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without saving.")
def patch_apply(source: str, target: str, overwrite: bool, dry_run: bool) -> None:
    """Apply variables from SOURCE onto TARGET."""
    try:
        result = apply_diff(source, target, overwrite=overwrite, dry_run=dry_run)
    except PatchError as exc:
        raise click.ClickException(str(exc))

    tag = " (dry-run)" if dry_run else ""
    click.echo(f"Patched '{target}' from '{source}'{tag}:")
    for k, v in sorted(result.items()):
        click.echo(f"  {k}={v}")
