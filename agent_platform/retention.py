"""Explicit privacy classification and dry-run-first trace retention."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .trace import TraceStore


@dataclass(frozen=True)
class RetentionPolicy:
    cutoff: str
    target: str = "operational_trace"
    version: str = "1"


def purge_trace(
    store: TraceStore, policy: RetentionPolicy, *, confirm: bool = False
) -> dict[str, Any]:
    """Preview or explicitly purge only local operational traces."""
    if policy.target != "operational_trace":
        raise ValueError("only operational_trace is an eligible target")
    datetime.fromisoformat(policy.cutoff.replace("Z", "+00:00"))
    with store._connect() as connection:
        rows = connection.execute(
            "SELECT run_id FROM runs WHERE created_at < ?", (policy.cutoff,)
        ).fetchall()
        run_ids = [row["run_id"] for row in rows]
        if confirm and run_ids:
            placeholders = ",".join("?" for _ in run_ids)
            connection.execute(
                f"DELETE FROM trace_references WHERE run_id IN ({placeholders})", run_ids
            )
            connection.execute(f"DELETE FROM events WHERE run_id IN ({placeholders})", run_ids)
            connection.execute(f"DELETE FROM runs WHERE run_id IN ({placeholders})", run_ids)
    return {
        "policy_version": policy.version,
        "target": policy.target,
        "cutoff": policy.cutoff,
        "candidate_count": len(run_ids),
        "deleted": len(run_ids) if confirm else 0,
        "dry_run": not confirm,
    }
