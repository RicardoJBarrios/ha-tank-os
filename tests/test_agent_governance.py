"""Tests for the complete agent governance checklist."""

from agent_platform.governance import CHECKS, evaluate_governance


def test_complete_evidence_passes_all_eleven_controls() -> None:
    evidence = {check.evidence_key: True for check in CHECKS}
    result = evaluate_governance(evidence, run_id="run-1")
    assert result["status"] == "pass"
    assert result["check_count"] == 11
    assert all(check["passed"] for check in result["checks"])
    assert result["product_owner_validation"] == "pending"


def test_missing_evidence_fails_closed_with_provenance() -> None:
    result = evaluate_governance({"secrets_scan_clean": True})
    assert result["status"] == "fail"
    failed = {check["evidence_key"] for check in result["checks"] if not check["passed"]}
    assert "main_unchanged" in failed
    assert "tool_recovery_verified" in failed
    assert all("evidence_key" in check for check in result["checks"])
