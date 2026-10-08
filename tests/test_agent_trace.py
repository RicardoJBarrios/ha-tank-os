"""Tests for local agent execution traceability."""

import json
import sqlite3
from datetime import timedelta
from pathlib import Path

import pytest

from agent_platform.trace import REDACTED, TraceError, TraceStore


def test_lifecycle_parent_child_and_integrity(tmp_path: Path) -> None:
    store = TraceStore(tmp_path / "trace.sqlite3")
    parent = store.start_run(agent_id="planner", provenance={"context_pack_key": "pack-1"})
    child = store.start_run(parent_run_id=parent["run_id"], agent_id="specialist")
    store.append_event(child["run_id"], "tool.completed", {"tool": "pytest", "result": "passed"})
    finished = store.finish(child["run_id"], "succeeded")

    assert finished["parent_run_id"] == parent["run_id"]
    assert finished["status"] == "succeeded"
    assert finished["integrity"]["valid"] is True
    assert len(finished["events"]) == 3


def test_rejects_invalid_lifecycle_operations(tmp_path: Path) -> None:
    store = TraceStore(tmp_path / "trace.sqlite3")
    run = store.start_run()["run_id"]
    store.finish(run, "cancelled")

    with pytest.raises(TraceError, match="terminal"):
        store.append_event(run, "late.event")
    with pytest.raises(TraceError, match="already terminal"):
        store.finish(run, "failed")


def test_redacts_persisted_and_exported_values(tmp_path: Path) -> None:
    store = TraceStore(tmp_path / "trace.sqlite3")
    run_id = store.start_run()["run_id"]
    store.append_event(
        run_id, "request.sent", {"Authorization": "Bearer super-secret-token", "message": "safe"}
    )
    exported = json.dumps(store.export(run_id))

    assert "super-secret-token" not in exported
    assert REDACTED in exported
    assert store.inspect(run_id)["events"][1]["redactions"] == ["Authorization"]


def test_redacts_bare_token_fields(tmp_path: Path) -> None:
    store = TraceStore(tmp_path / "trace.sqlite3")
    run_id = store.start_run(agent_id="test")["run_id"]

    event = store.append_event(run_id, "request.sent", {"token": "secret-value"})

    assert event["payload"] == {"token": "[REDACTED]"}
    assert event["redactions"] == ["token"]


def test_verification_reports_tampering(tmp_path: Path) -> None:
    path = tmp_path / "trace.sqlite3"
    store = TraceStore(path)
    run_id = store.start_run()["run_id"]
    store.append_event(run_id, "observation", {"value": 1})
    with sqlite3.connect(path) as connection:
        connection.execute(
            "UPDATE events SET payload_json = ? WHERE run_id = ? AND sequence = 2",
            ('{"value":99}', run_id),
        )
        connection.commit()

    result = store.verify(run_id)
    assert result.valid is False
    assert result.first_error == {"sequence": 2, "expected_sequence": 2}


def test_missing_references_are_preserved_and_recovery_is_explicit(tmp_path: Path) -> None:
    store = TraceStore(tmp_path / "trace.sqlite3")
    run_id = store.start_run()["run_id"]
    reference = store.add_reference(
        run_id, "artifact", "missing/report.json", verification_status="missing"
    )
    assert reference["verification_status"] == "missing"

    with pytest.raises(TraceError, match="not stale"):
        store.recover(run_id, stale_after=timedelta(days=1), reason="test")

    with store._connect() as connection:
        connection.execute(
            "UPDATE runs SET created_at = ? WHERE run_id = ?", ("2000-01-01T00:00:00Z", run_id)
        )
        connection.commit()
    recovered = store.recover(
        run_id, stale_after=timedelta(seconds=1), reason="interrupted local run"
    )
    assert recovered["status"] == "abandoned"
    assert recovered["references"][0]["locator"] == "missing/report.json"
    assert recovered["integrity"]["valid"] is True
