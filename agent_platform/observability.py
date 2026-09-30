"""Bounded, read-only metrics derived from the local trace store."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .trace import TRACE_SCHEMA, TraceStore, utc_now

OBSERVABILITY_SCHEMA = "agent-observability/v1"


def snapshot(
    store: TraceStore,
    *,
    start: datetime,
    end: datetime,
    max_rows: int = 10_000,
) -> dict[str, Any]:
    """Build a bounded metrics snapshot without returning event payloads."""
    if start.tzinfo is None or end.tzinfo is None or start >= end:
        raise ValueError("start and end must be timezone-aware and start before end")
    if max_rows <= 0:
        raise ValueError("max_rows must be positive")
    start_text = start.astimezone(UTC).isoformat().replace("+00:00", "Z")
    end_text = end.astimezone(UTC).isoformat().replace("+00:00", "Z")
    with store._connect() as connection:
        runs = connection.execute(
            "SELECT run_id, status, created_at, completed_at FROM runs WHERE created_at >= ? AND created_at < ? ORDER BY created_at LIMIT ?",
            (start_text, end_text, max_rows + 1),
        ).fetchall()
        truncated = len(runs) > max_rows
        runs = runs[:max_rows]
        run_ids = [row["run_id"] for row in runs]
        events = []
        if run_ids:
            placeholders = ",".join("?" for _ in run_ids)
            events = connection.execute(
                f"SELECT event_type FROM events WHERE run_id IN ({placeholders}) AND occurred_at >= ? AND occurred_at < ? ORDER BY occurred_at LIMIT ?",
                (*run_ids, start_text, end_text, max_rows + 1),
            ).fetchall()
    event_truncated = len(events) > max_rows
    events = events[:max_rows]
    durations: list[float] = []
    invalid_durations = 0
    for row in runs:
        if not row["completed_at"]:
            continue
        try:
            created = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
            completed = datetime.fromisoformat(row["completed_at"].replace("Z", "+00:00"))
            duration = (completed - created).total_seconds()
            if duration >= 0:
                durations.append(duration)
            else:
                invalid_durations += 1
        except ValueError:
            invalid_durations += 1
    durations.sort()
    status_counts = Counter(str(row["status"]) for row in runs)
    event_counts = Counter(str(row["event_type"]) for row in events)
    return {
        "schema": OBSERVABILITY_SCHEMA,
        "generated_at": utc_now(),
        "source_schema": TRACE_SCHEMA,
        "source_store": str(store.path),
        "window": {"start": start_text, "end": end_text},
        "coverage": {
            "runs": len(runs),
            "events": len(events),
            "truncated": truncated or event_truncated,
            "max_rows": max_rows,
        },
        "runs_by_status": dict(sorted(status_counts.items())),
        "event_counts": dict(sorted(event_counts.items())),
        "durations_seconds": {
            "count": len(durations),
            "min": durations[0] if durations else None,
            "max": durations[-1] if durations else None,
            "p50": durations[(len(durations) - 1) // 2] if durations else None,
            "invalid": invalid_durations,
        },
    }


def cli(argv: list[str] | None = None) -> int:
    """CLI for a local observability snapshot."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate bounded agent observability metrics")
    parser.add_argument("--store", type=Path)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--max-rows", type=int, default=10_000)
    args = parser.parse_args(argv)
    result = snapshot(
        TraceStore(args.store),
        start=datetime.fromisoformat(args.start.replace("Z", "+00:00")),
        end=datetime.fromisoformat(args.end.replace("Z", "+00:00")),
        max_rows=args.max_rows,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0
