"""Integration helper: register freeze commands into the main envctl CLI."""

from __future__ import annotations

import click

from envctl.cli_freeze import cmd_freeze


def register_freeze(cli: click.Group) -> None:
    """Attach the freeze command group to *cli*."""
    cli.add_command(cmd_freeze)


def _demo_cli() -> click.Group:
    """Return a minimal standalone CLI for manual testing."""

    @click.group()
    def _cli() -> None:
        """envctl freeze demo."""

    register_freeze(_cli)
    return _cli


if __name__ == "__main__":  # pragma: no cover
    _demo_cli()()
