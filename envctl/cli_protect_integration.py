"""Register the protect command group into the main envctl CLI."""

from __future__ import annotations

import click

from envctl.cli_protect import cmd_protect


def register_protect(cli: click.Group) -> None:
    """Attach the ``protect`` command group to *cli*."""
    cli.add_command(cmd_protect)


# ---------------------------------------------------------------------------
# Minimal standalone demo (not used in production)
# ---------------------------------------------------------------------------

@click.group()
def _demo_cli() -> None:  # pragma: no cover
    """Demo wrapper for manual testing."""


register_protect(_demo_cli)  # type: ignore[arg-type]

if __name__ == "__main__":  # pragma: no cover
    _demo_cli()
