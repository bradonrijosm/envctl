"""CLI commands for running built-in pipelines against a profile."""
import click

from envctl.pipeline import (
    Pipeline,
    PipelineError,
    apply_pipeline,
    step_filter_keys,
    step_prefix_keys,
    step_uppercase_values,
)


@click.group(name="pipeline")
def cmd_pipeline():
    """Apply transformation pipelines to profiles."""


@cmd_pipeline.command(name="prefix-keys")
@click.argument("profile")
@click.argument("prefix")
def pipeline_prefix_keys(profile: str, prefix: str):
    """Prefix every key in PROFILE with PREFIX."""
    pipeline = Pipeline("prefix-keys").add_step("prefix", step_prefix_keys(prefix))
    try:
        result = apply_pipeline(profile, pipeline)
        click.echo(f"Updated {len(result)} key(s) in '{profile}'.")
    except PipelineError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_pipeline.command(name="uppercase-values")
@click.argument("profile")
def pipeline_uppercase_values(profile: str):
    """Uppercase every value in PROFILE."""
    pipeline = Pipeline("uppercase-values").add_step("upper", step_uppercase_values())
    try:
        result = apply_pipeline(profile, pipeline)
        click.echo(f"Updated {len(result)} key(s) in '{profile}'.")
    except PipelineError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cmd_pipeline.command(name="filter-keys")
@click.argument("profile")
@click.argument("keys", nargs=-1, required=True)
def pipeline_filter_keys(profile: str, keys: tuple):
    """Keep only the specified KEYS in PROFILE."""
    pipeline = Pipeline("filter-keys").add_step("filter", step_filter_keys(list(keys)))
    try:
        result = apply_pipeline(profile, pipeline)
        click.echo(f"Kept {len(result)} key(s) in '{profile}'.")
    except PipelineError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
