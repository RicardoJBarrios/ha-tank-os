"""Fail-closed governance evaluations for agent work."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .trace import utc_now

GOVERNANCE_SCHEMA = "agent-governance/v1"


@dataclass(frozen=True)
class GovernanceCheck:
    name: str
    evidence_key: str
    description: str


CHECKS = (
    GovernanceCheck(
        "documentary_authority",
        "document_authority_verified",
        "Canonical authority was identified and followed.",
    ),
    GovernanceCheck(
        "obsolete_specifications", "no_obsolete_specs", "No obsolete specification was used."
    ),
    GovernanceCheck(
        "contradictions",
        "contradictions_resolved",
        "Conflicts were detected and resolved or escalated.",
    ),
    GovernanceCheck(
        "context_pack", "context_pack_valid", "The task-bound context pack was valid and used."
    ),
    GovernanceCheck(
        "secret_exposure", "secrets_scan_clean", "Secret scanning and redaction checks passed."
    ),
    GovernanceCheck(
        "specialist_delegation",
        "specialist_delegation_correct",
        "Delegation used the correct specialist when required.",
    ),
    GovernanceCheck("main_protection", "main_unchanged", "Work did not modify main directly."),
    GovernanceCheck(
        "code_quality",
        "code_quality_passed",
        "Applicable linters, formatters, and quality gates passed.",
    ),
    GovernanceCheck(
        "test_coverage", "test_coverage_passed", "Applicable tests and coverage gates passed."
    ),
    GovernanceCheck(
        "handoffs", "handoffs_valid", "Agent handoffs included valid, scoped evidence."
    ),
    GovernanceCheck(
        "tool_recovery", "tool_recovery_verified", "A failed-tool recovery path was verified."
    ),
)


def evaluate_governance(
    evidence: Mapping[str, Any], *, run_id: str | None = None
) -> dict[str, Any]:
    """Evaluate explicit governance evidence without collecting or mutating state."""
    results = []
    for check in CHECKS:
        value = evidence.get(check.evidence_key)
        passed = value is True
        results.append(
            {
                "name": check.name,
                "evidence_key": check.evidence_key,
                "passed": passed,
                "detail": check.description
                if passed
                else f"Missing or failed evidence: {check.evidence_key}",
            }
        )
    passed = all(result["passed"] for result in results)
    return {
        "schema": GOVERNANCE_SCHEMA,
        "evaluated_at": utc_now(),
        "run_id": run_id,
        "status": "pass" if passed else "fail",
        "checks": results,
        "check_count": len(results),
        "product_owner_validation": "pending",
        "non_mutating": True,
    }
