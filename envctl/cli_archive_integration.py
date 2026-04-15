"""Register archive commands into the main envctl CLI group."""
from __future__ import annotations

import click

from envctl.cli_archive import cmd_archive


def register_archive(cli: click.Group) -> None:
    """Attach the archive command group to *cli*."""
    cli.add_command(cmd_archive)


# ---------------------------------------------------------------------------
# Minimal demo entry-point (used for manual smoke-testing)
# ---------------------------------------------------------------------------

@click.group()
def _demo_cli() -> None:  # pragma: no cover
    """envctl demo with archive commands."""


register_archive(_demo_cli)


if __name__ == "__main__":  # pragma: no cover
    _demo_cli()
