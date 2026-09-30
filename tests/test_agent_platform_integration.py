"""Integration coverage proving the agent-platform controls compose."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

from agent_platform.evaluation import EvaluationCase, evaluate
from agent_platform.governance import CHECKS, evaluate_governance
from agent_platform.lineage import create_manifest, verify_manifest
from agent_platform.observability import snapshot
from agent_platform.policy import Policy, Rule
from agent_platform.reliability import FailureClass, ReliabilityPolicy
from agent_platform.retention import RetentionPolicy, purge_trace
from agent_platform.trace import TraceStore


def test_platform_controls_share_one_traced_execution(tmp_path: Path) -> None:
    store = TraceStore(tmp_path / "trace.sqlite3")
    run_id = store.start_run(agent_id="integration", provenance={"context_pack_key": "pack-1"})[
        "run_id"
    ]
    policy = Policy([Rule("read", "ha.read", "entity:*", "allow")])
    assert (
        policy.evaluate("ha.read", "entity:light.kitchen", run_id=run_id, trace=store)["decision"]
        == "allow"
    )
    assert (
        ReliabilityPolicy().decide(FailureClass.TRANSIENT, attempt=1, idempotent=True)["decision"]
        == "retry"
    )
    evaluation = evaluate(
        EvaluationCase("smoke", "1", required_markers=("safe",)),
        status="succeeded",
        summary="safe",
        duration_seconds=0.1,
        run_id=run_id,
    )
    assert evaluation["status"] == "pass"
    evidence = {check.evidence_key: True for check in CHECKS}
    assert evaluate_governance(evidence, run_id=run_id)["status"] == "pass"
    artifact = tmp_path / "evidence.json"
    artifact.write_text("safe\n")
    assert (
        verify_manifest(
            create_manifest("evidence", "evaluation", str(artifact), producer_run_id=run_id)
        ).status
        == "verified"
    )
    now = datetime.now(UTC)
    assert (
        snapshot(store, start=now - timedelta(minutes=1), end=now + timedelta(minutes=1))[
            "coverage"
        ]["runs"]
        == 1
    )
    assert purge_trace(store, RetentionPolicy("2000-01-01T00:00:00Z"))["candidate_count"] == 0
