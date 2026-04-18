"""Scheduled/timed export: export a profile to a file on a cron-like interval."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from envctl.export import export_profile
from envctl.storage import get_profile


class ScheduleError(Exception):
    pass


@dataclass
class ScheduleConfig:
    profile: str
    output_path: Path
    fmt: str = "dotenv"
    interval: int = 60  # seconds
    max_runs: Optional[int] = None
    on_write: Callable[[Path], None] = field(default=lambda p: None)


def _write_export(config: ScheduleConfig) -> None:
    """Render profile and write to output_path."""
    profile = get_profile(config.profile)
    if profile is None:
        raise ScheduleError(f"Profile '{config.profile}' not found.")
    content = export_profile(profile, fmt=config.fmt)
    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    config.output_path.write_text(content)
    config.on_write(config.output_path)


def run_schedule(config: ScheduleConfig, _sleep: Callable[[float], None] = time.sleep) -> None:
    """Run export on a fixed interval. Blocks until max_runs reached (or forever)."""
    runs = 0
    while True:
        _write_export(config)
        runs += 1
        if config.max_runs is not None and runs >= config.max_runs:
            break
        _sleep(config.interval)
