"""Integration helpers: register cmd_watch into the main CLI.

Import this module in cli.py to attach the watch command group::

    from envctl.cli_watch_integration import register_watch
    register_watch(cli)
"""

from __future__ import annotations

import click

from envctl.cli_watch import cmd_watch


def register_watch(cli: click.Group) -> None:
    """Attach the *watch* command group to *cli*."""
    cli.add_command(cmd_watch)


# Allow direct execution for quick smoke-testing:
# python -m envctl.cli_watch_integration
if __name__ == "__main__":  # pragma: no cover
    @click.group()
    def _demo_cli() -> None:
        """Demo CLI."""

    register_watch(_demo_cli)
    _demo_cli()
