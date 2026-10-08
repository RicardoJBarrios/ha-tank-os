"""Deterministic local evaluation of structured agent results."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .trace import TRACE_SCHEMA, redact, utc_now

EVALUATION_SCHEMA = "agent-evaluation/v1"
MAX_SUMMARY_LENGTH = 20_000


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    version: str
    expected_status: str = "succeeded"
    required_markers: tuple[str, ...] = ()
    forbidden_markers: tuple[str, ...] = ()
    max_duration_seconds: float | None = None


def evaluate(
    case: EvaluationCase,
    *,
    status: str,
    summary: str,
    duration_seconds: float,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Evaluate a bounded result without invoking an agent or tool."""
    safe_summary, redactions = redact(summary[:MAX_SUMMARY_LENGTH])
    checks: list[dict[str, Any]] = []
    checks.append(
        {
            "name": "status",
            "passed": status == case.expected_status,
            "expected": case.expected_status,
            "actual": status,
        }
    )
    checks.extend(
        {"name": f"required:{marker}", "passed": marker in safe_summary}
        for marker in case.required_markers
    )
    checks.extend(
        {"name": f"forbidden:{marker}", "passed": marker not in safe_summary}
        for marker in case.forbidden_markers
    )
    if case.max_duration_seconds is not None:
        checks.append(
            {
                "name": "latency",
                "passed": duration_seconds <= case.max_duration_seconds,
                "max": case.max_duration_seconds,
                "actual": duration_seconds,
            }
        )
    passed = all(bool(check["passed"]) for check in checks)
    return {
        "schema": EVALUATION_SCHEMA,
        "source_trace_schema": TRACE_SCHEMA,
        "case": asdict(case),
        "run_id": run_id,
        "evaluated_at": utc_now(),
        "duration_seconds": duration_seconds,
        "status": "pass" if passed else "fail",
        "checks": checks,
        "summary": safe_summary,
        "redactions": redactions,
        "product_owner_validation": "pending",
    }
