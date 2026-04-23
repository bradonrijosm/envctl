"""cli_chain_integration.py – Register the chain command group with the root CLI."""
from __future__ import annotations

import click

from envctl.cli_chain import cmd_chain


def register_chain(root: click.Group) -> None:
    """Attach the 'chain' sub-group to *root*."""
    root.add_command(cmd_chain)


# ---------------------------------------------------------------------------
# Standalone demo (python -m envctl.cli_chain_integration)
# ---------------------------------------------------------------------------

def _demo_cli() -> click.Group:
    @click.group()
    def _cli():
        """envctl demo with chain support."""

    register_chain(_cli)
    return _cli


if __name__ == "__main__":  # pragma: no cover
    _demo_cli()()
