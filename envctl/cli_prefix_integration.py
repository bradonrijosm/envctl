"""Register the `prefix` command group into the main envctl CLI."""

from __future__ import annotations

import click

from envctl.cli_prefix import cmd_prefix


def register_prefix(cli: click.Group) -> None:
    """Attach the `prefix` command group to *cli*.

    Call this from the application entry-point after all other
    commands have been registered::

        from envctl.cli_prefix_integration import register_prefix
        register_prefix(cli)
    """
    cli.add_command(cmd_prefix)


# ---------------------------------------------------------------------------
# Minimal standalone demo (not part of the real CLI entry-point)
# ---------------------------------------------------------------------------

def _demo_cli() -> click.Group:  # pragma: no cover
    @click.group()
    def _cli():
        """envctl demo."""

    register_prefix(_cli)
    return _cli


if __name__ == "__main__":  # pragma: no cover
    _demo_cli()()
