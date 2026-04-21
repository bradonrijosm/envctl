"""Backup and restore individual profiles to/from JSON files."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from envctl.storage import get_profile, set_profile, load_profiles


class BackupError(Exception):
    """Raised when a backup or restore operation fails."""


def backup_profile(profile_name: str, dest_dir: str, label: Optional[str] = None) -> str:
    """Export a single profile to a JSON file in *dest_dir*.

    Returns the path of the written file.
    """
    variables = get_profile(profile_name)
    if variables is None:
        raise BackupError(f"Profile '{profile_name}' does not exist.")

    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = f"_{label}" if label else ""
    filename = f"{profile_name}{suffix}_{ts}.json"
    filepath = dest / filename

    payload = {
        "profile": profile_name,
        "exported_at": ts,
        "label": label,
        "variables": variables,
    }
    filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(filepath)


def restore_profile(backup_path: str, overwrite: bool = False) -> str:
    """Import a profile from a JSON backup file.

    Returns the profile name that was restored.
    """
    path = Path(backup_path)
    if not path.is_file():
        raise BackupError(f"Backup file not found: {backup_path}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BackupError(f"Invalid backup file: {exc}") from exc

    profile_name: str = payload.get("profile", "")
    variables: Dict[str, str] = payload.get("variables", {})

    if not profile_name:
        raise BackupError("Backup file is missing the 'profile' field.")

    existing = get_profile(profile_name)
    if existing is not None and not overwrite:
        raise BackupError(
            f"Profile '{profile_name}' already exists. Use overwrite=True to replace it."
        )

    set_profile(profile_name, variables)
    return profile_name


def list_backups(backup_dir: str) -> list[Dict]:
    """List all backup files in *backup_dir*, newest first."""
    directory = Path(backup_dir)
    if not directory.is_dir():
        return []

    entries = []
    for fp in sorted(directory.glob("*.json"), reverse=True):
        try:
            payload = json.loads(fp.read_text(encoding="utf-8"))
            entries.append(
                {
                    "file": fp.name,
                    "path": str(fp),
                    "profile": payload.get("profile", "?"),
                    "exported_at": payload.get("exported_at", "?"),
                    "label": payload.get("label"),
                }
            )
        except (json.JSONDecodeError, OSError):
            continue
    return entries
