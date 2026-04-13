"""CLI commands for encrypted profile storage."""

import click

from envctl.encrypt import (
    EncryptError,
    store_encrypted_profile,
    load_encrypted_profile,
    delete_encrypted_profile,
    list_encrypted_profiles,
)
from envctl.storage import get_profile
from envctl.export import export_bash


@click.group("encrypt")
def cmd_encrypt():
    """Manage encrypted profile storage."""


@cmd_encrypt.command("store")
@click.argument("profile")
@click.password_option("--passphrase", prompt="Passphrase", help="Encryption passphrase.")
def encrypt_store(profile: str, passphrase: str):
    """Encrypt and store a profile's variables."""
    data = get_profile(profile)
    if data is None:
        click.echo(f"Error: profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    try:
        store_encrypted_profile(profile, data, passphrase)
        click.echo(f"Profile '{profile}' encrypted and stored.")
    except EncryptError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_encrypt.command("load")
@click.argument("profile")
@click.option("--passphrase", prompt="Passphrase", hide_input=True, help="Decryption passphrase.")
@click.option("--format", "fmt", default="bash", show_default=True,
              type=click.Choice(["bash", "raw"]), help="Output format.")
def encrypt_load(profile: str, passphrase: str, fmt: str):
    """Decrypt and display a stored encrypted profile."""
    try:
        variables = load_encrypted_profile(profile, passphrase)
    except EncryptError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if fmt == "bash":
        click.echo(export_bash(variables))
    else:
        for k, v in variables.items():
            click.echo(f"{k}={v}")


@cmd_encrypt.command("delete")
@click.argument("profile")
def encrypt_delete(profile: str):
    """Remove a stored encrypted profile."""
    try:
        delete_encrypted_profile(profile)
        click.echo(f"Encrypted profile '{profile}' deleted.")
    except EncryptError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_encrypt.command("list")
def encrypt_list():
    """List all stored encrypted profiles."""
    names = list_encrypted_profiles()
    if not names:
        click.echo("No encrypted profiles stored.")
    else:
        for name in sorted(names):
            click.echo(name)
