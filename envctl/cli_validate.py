"""CLI integration for profile and variable validation (cmd_validate)."""

import click
from envctl.storage import load_profiles
from envctl.validate import (
    ValidationError,
    validate_profile_name,
    validate_variables,
)


@click.command('validate')
@click.argument('profile_name')
@click.option(
    '--allow-reserved',
    is_flag=True,
    default=False,
    help='Allow reserved shell variable names (e.g. PATH, HOME).',
)
def cmd_validate(profile_name: str, allow_reserved: bool) -> None:
    """Validate the name and variables of an existing profile.

    Exits with status 1 if validation fails, 0 on success.
    """
    # Validate the profile name itself first
    try:
        validate_profile_name(profile_name)
    except ValidationError as exc:
        raise click.ClickException(str(exc)) from exc

    # Load the profile from the store
    profiles = load_profiles()
    if profile_name not in profiles:
        raise click.ClickException(f"Profile '{profile_name}' not found.")

    variables: dict = profiles[profile_name].get('variables', {})

    if not variables:
        click.echo(f"Profile '{profile_name}' has no variables — nothing to validate.")
        return

    try:
        validate_variables(variables, allow_reserved=allow_reserved)
    except ValidationError as exc:
        bad = ', '.join(exc.invalid_keys)
        raise click.ClickException(
            f"Validation failed for profile '{profile_name}': {exc}\n"
            f"  Offending key(s): {bad}"
        ) from exc

    click.echo(
        click.style(
            f"✓ Profile '{profile_name}' is valid ({len(variables)} variable(s)).",
            fg='green',
        )
    )
