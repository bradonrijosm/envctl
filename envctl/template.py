"""Template rendering for environment variable profiles.

Allows profiles to reference other profiles' variables using
{{PROFILE.VAR_NAME}} or {{VAR_NAME}} (current profile) syntax.
"""

import re
from typing import Dict

from envctl.storage import load_profiles

TEMPLATE_PATTERN = re.compile(r"\{\{([A-Z_][A-Z0-9_]*)(?:\.([A-Z_][A-Z0-9_]*))?\}\}")


class TemplateError(Exception):
    """Raised when template rendering fails."""


def render_value(value: str, context: Dict[str, str], all_profiles: Dict[str, Dict[str, str]]) -> str:
    """Render a single value, resolving {{VAR}} and {{PROFILE.VAR}} references."""

    def replacer(match: re.Match) -> str:
        first, second = match.group(1), match.group(2)
        if second is None:
            # {{VAR_NAME}} — look up in current profile context
            if first not in context:
                raise TemplateError(f"Undefined variable reference: '{{{{{first}}}}}'")
            return context[first]
        else:
            # {{PROFILE.VAR_NAME}} — first is profile name, second is var
            profile_name, var_name = first, second
            if profile_name not in all_profiles:
                raise TemplateError(f"Unknown profile in template reference: '{profile_name}'")
            profile_vars = all_profiles[profile_name]
            if var_name not in profile_vars:
                raise TemplateError(
                    f"Variable '{var_name}' not found in profile '{profile_name}'"
                )
            return profile_vars[var_name]

    return TEMPLATE_PATTERN.sub(replacer, value)


def render_profile(profile_name: str) -> Dict[str, str]:
    """Render all variables in a profile, resolving template references.

    Returns a new dict with all references expanded.
    Raises TemplateError if a reference cannot be resolved.
    """
    all_profiles = load_profiles()
    if profile_name not in all_profiles:
        raise TemplateError(f"Profile '{profile_name}' does not exist.")

    raw_vars = all_profiles[profile_name]
    rendered: Dict[str, str] = {}

    for key, value in raw_vars.items():
        rendered[key] = render_value(value, raw_vars, all_profiles)

    return rendered
