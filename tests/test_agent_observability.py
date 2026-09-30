"""Tests for bounded derived agent metrics."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

from agent_platform.observability import snapshot
from agent_platform.trace import TraceStore


def test_snapshot_counts_statuses_events_and_durations(tmp_path: Path) -> None:
    store = TraceStore(tmp_path / "trace.sqlite3")
    run_id = store.start_run()["run_id"]
    store.append_event(run_id, "tool.completed", {"secret": "do-not-export"})
    store.finish(run_id, "succeeded")
    now = datetime.now(UTC)
    result = snapshot(store, start=now - timedelta(minutes=1), end=now + timedelta(minutes=1))

    assert result["runs_by_status"] == {"succeeded": 1}
    assert result["event_counts"]["tool.completed"] == 1
    assert result["durations_seconds"]["count"] == 1
    assert "do-not-export" not in str(result)


def test_snapshot_reports_empty_and_truncated_windows(tmp_path: Path) -> None:
    store = TraceStore(tmp_path / "trace.sqlite3")
    for _ in range(2):
        run_id = store.start_run()["run_id"]
        store.finish(run_id, "failed", reason="test")
    now = datetime.now(UTC)
    empty = snapshot(store, start=now + timedelta(days=1), end=now + timedelta(days=2))
    limited = snapshot(
        store, start=now - timedelta(minutes=1), end=now + timedelta(minutes=1), max_rows=1
    )

    assert empty["runs_by_status"] == {}
    assert empty["coverage"]["truncated"] is False
    assert limited["coverage"]["truncated"] is True
