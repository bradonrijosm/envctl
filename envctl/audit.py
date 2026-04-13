"""Audit log for tracking profile mutations (create, update, delete, import)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional

from envctl.storage import get_store_path


class AuditError(Exception):
    """Raised when an audit log operation fails."""


_AUDIT_FILE = "audit.json"
_MAX_ENTRIES = 500


def _get_audit_path() -> Path:
    return get_store_path() / _AUDIT_FILE


def _load_audit() -> List[dict]:
    path = _get_audit_path()
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise AuditError(f"Failed to read audit log: {exc}") from exc


def _save_audit(entries: List[dict]) -> None:
    path = _get_audit_path()
    try:
        path.write_text(json.dumps(entries, indent=2))
    except OSError as exc:
        raise AuditError(f"Failed to write audit log: {exc}") from exc


def record_event(action: str, profile: str, detail: Optional[str] = None) -> None:
    """Append an audit event. Trims log to _MAX_ENTRIES."""
    entries = _load_audit()
    entry = {
        "timestamp": time.time(),
        "action": action,
        "profile": profile,
    }
    if detail:
        entry["detail"] = detail
    entries.append(entry)
    if len(entries) > _MAX_ENTRIES:
        entries = entries[-_MAX_ENTRIES:]
    _save_audit(entries)


def get_audit_log(profile: Optional[str] = None, limit: int = 50) -> List[dict]:
    """Return audit entries, newest first. Optionally filter by profile name."""
    entries = _load_audit()
    if profile:
        entries = [e for e in entries if e.get("profile") == profile]
    return list(reversed(entries))[:limit]


def clear_audit_log() -> int:
    """Remove all audit entries. Returns the count of removed entries."""
    entries = _load_audit()
    count = len(entries)
    _save_audit([])
    return count
