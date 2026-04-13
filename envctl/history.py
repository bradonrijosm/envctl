"""Track and manage profile activation history."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from envctl.storage import get_store_path

HISTORY_FILE = "history.json"
MAX_HISTORY = 50


class HistoryError(Exception):
    """Raised when a history operation fails."""


def _get_history_path() -> Path:
    return get_store_path().parent / HISTORY_FILE


def _load_history() -> List[dict]:
    path = _get_history_path()
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise HistoryError(f"Failed to load history: {exc}") from exc


def _save_history(entries: List[dict]) -> None:
    path = _get_history_path()
    try:
        path.write_text(json.dumps(entries, indent=2))
    except OSError as exc:
        raise HistoryError(f"Failed to save history: {exc}") from exc


def record_activation(profile_name: str) -> None:
    """Append an activation event for *profile_name* to the history log."""
    entries = _load_history()
    entries.append({
        "profile": profile_name,
        "activated_at": datetime.now(timezone.utc).isoformat(),
    })
    # Keep only the most recent MAX_HISTORY entries
    entries = entries[-MAX_HISTORY:]
    _save_history(entries)


def get_history(limit: Optional[int] = None) -> List[dict]:
    """Return activation history, newest first.

    Args:
        limit: Maximum number of entries to return.  ``None`` returns all.
    """
    entries = list(reversed(_load_history()))
    if limit is not None:
        entries = entries[:limit]
    return entries


def clear_history() -> None:
    """Remove all history entries."""
    _save_history([])


def last_activated() -> Optional[str]:
    """Return the name of the most recently activated profile, or ``None``."""
    entries = _load_history()
    if not entries:
        return None
    return entries[-1]["profile"]
