"""Tests for deterministic agent evaluation."""

from agent_platform.evaluation import EvaluationCase, evaluate


def test_evaluation_passes_and_keeps_owner_validation_pending() -> None:
    result = evaluate(
        EvaluationCase("smoke", "1", required_markers=("safe",)),
        status="succeeded",
        summary="safe result",
        duration_seconds=0.2,
        run_id="run-1",
    )
    assert result["status"] == "pass"
    assert result["product_owner_validation"] == "pending"


def test_evaluation_reports_failures_and_redacts_summary() -> None:
    case = EvaluationCase(
        "safety",
        "1",
        required_markers=("safe",),
        forbidden_markers=("danger",),
        max_duration_seconds=1,
    )
    result = evaluate(
        case, status="failed", summary="danger token=sk_123456789", duration_seconds=2
    )
    assert result["status"] == "fail"
    assert any(not check["passed"] for check in result["checks"])
    assert "sk_123456789" not in str(result)
