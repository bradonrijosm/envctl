"""Archive and restore full environment profile stores."""
from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from envctl.storage import get_store_path, load_profiles, save_profiles


class ArchiveError(Exception):
    """Raised when an archive operation fails."""


_MANIFEST_NAME = "envctl_manifest.json"
_PROFILES_NAME = "profiles.json"


def create_archive(dest: Path, label: str = "") -> Path:
    """Write all current profiles into a zip archive at *dest*.

    Returns the resolved path of the created archive.
    """
    profiles = load_profiles()
    if dest.suffix != ".zip":
        dest = dest.with_suffix(".zip")
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "label": label,
        "profile_count": len(profiles),
    }
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(_MANIFEST_NAME, json.dumps(manifest, indent=2))
        zf.writestr(_PROFILES_NAME, json.dumps(profiles, indent=2))
    return dest.resolve()


def restore_archive(src: Path, overwrite: bool = False) -> dict:
    """Load profiles from *src* archive into the active store.

    If *overwrite* is False, existing profiles are kept and only new ones
    from the archive are added.  Returns the manifest dict.
    """
    if not src.exists():
        raise ArchiveError(f"Archive not found: {src}")
    with zipfile.ZipFile(src, "r") as zf:
        names = zf.namelist()
        if _PROFILES_NAME not in names:
            raise ArchiveError("Archive is missing profiles.json")
        archived: dict = json.loads(zf.read(_PROFILES_NAME))
        manifest: dict = (
            json.loads(zf.read(_MANIFEST_NAME)) if _MANIFEST_NAME in names else {}
        )
    current = load_profiles()
    if overwrite:
        current.update(archived)
    else:
        for name, data in archived.items():
            if name not in current:
                current[name] = data
    save_profiles(current)
    return manifest


def inspect_archive(src: Path) -> dict:
    """Return the manifest and list of profile names from *src* without restoring."""
    if not src.exists():
        raise ArchiveError(f"Archive not found: {src}")
    with zipfile.ZipFile(src, "r") as zf:
        names = zf.namelist()
        if _PROFILES_NAME not in names:
            raise ArchiveError("Archive is missing profiles.json")
        profiles: dict = json.loads(zf.read(_PROFILES_NAME))
        manifest: dict = (
            json.loads(zf.read(_MANIFEST_NAME)) if _MANIFEST_NAME in names else {}
        )
    return {"manifest": manifest, "profiles": list(profiles.keys())}
