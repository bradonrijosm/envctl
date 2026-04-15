"""Register group commands into the main CLI."""
from __future__ import annotations

import click

from envctl.cli_group import cmd_group


def register_group(cli: click.Group) -> None:
    """Attach the group sub-command tree to *cli*."""
    cli.add_command(cmd_group)


if __name__ == "__main__":  # pragma: no cover
    # Quick smoke-test: python -m envctl.cli_group_integration
    @click.group()
    def _demo_cli():
        pass

    register_group(_demo_cli)
    _demo_cli()
