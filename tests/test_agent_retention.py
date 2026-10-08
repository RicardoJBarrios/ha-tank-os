"""Tests for explicit trace retention."""

from pathlib import Path

import pytest

from agent_platform.retention import RetentionPolicy, purge_trace
from agent_platform.trace import TraceStore


def test_retention_is_dry_run_by_default_and_idempotent(tmp_path: Path) -> None:
    store = TraceStore(tmp_path / "trace.sqlite3")
    store.start_run()
    policy = RetentionPolicy("2999-01-01T00:00:00Z")
    preview = purge_trace(store, policy)
    assert preview["dry_run"] is True
    assert preview["deleted"] == 0
    deleted = purge_trace(store, policy, confirm=True)
    assert deleted["deleted"] == 1
    assert purge_trace(store, policy, confirm=True)["deleted"] == 0


def test_retention_rejects_non_trace_targets(tmp_path: Path) -> None:
    store = TraceStore(tmp_path / "trace.sqlite3")
    with pytest.raises(ValueError, match="operational_trace"):
        purge_trace(store, RetentionPolicy("2999-01-01T00:00:00Z", target="product_data"))
