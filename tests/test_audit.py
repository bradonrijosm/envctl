"""Tests for envctl.audit module."""

from __future__ import annotations

import pytest

from envctl.audit import (
    AuditError,
    clear_audit_log,
    get_audit_log,
    record_event,
)


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envctl.storage._STORE_DIR", tmp_path)
    monkeypatch.setattr("envctl.audit._get_audit_path", lambda: tmp_path / "audit.json")
    yield tmp_path


def test_get_audit_log_empty():
    assert get_audit_log() == []


def test_record_event_creates_entry():
    record_event("create", "dev")
    log = get_audit_log()
    assert len(log) == 1
    assert log[0]["action"] == "create"
    assert log[0]["profile"] == "dev"
    assert "timestamp" in log[0]


def test_record_event_with_detail():
    record_event("update", "staging", detail="merged from prod")
    log = get_audit_log()
    assert log[0]["detail"] == "merged from prod"


def test_get_audit_log_newest_first():
    record_event("create", "alpha")
    record_event("update", "beta")
    record_event("delete", "gamma")
    log = get_audit_log()
    assert log[0]["profile"] == "gamma"
    assert log[1]["profile"] == "beta"
    assert log[2]["profile"] == "alpha"


def test_get_audit_log_filter_by_profile():
    record_event("create", "dev")
    record_event("create", "prod")
    record_event("update", "dev")
    log = get_audit_log(profile="dev")
    assert all(e["profile"] == "dev" for e in log)
    assert len(log) == 2


def test_get_audit_log_respects_limit():
    for i in range(10):
        record_event("create", f"profile-{i}")
    log = get_audit_log(limit=3)
    assert len(log) == 3


def test_clear_audit_log_returns_count():
    record_event("create", "dev")
    record_event("update", "dev")
    removed = clear_audit_log()
    assert removed == 2
    assert get_audit_log() == []


def test_clear_audit_log_empty_returns_zero():
    assert clear_audit_log() == 0
