"""Tests for explicit agent authorization."""

from datetime import timedelta
from pathlib import Path

from agent_platform.policy import Policy, Rule
from agent_platform.trace import TraceStore


def test_policy_is_explicit_and_deny_by_default() -> None:
    policy = Policy(
        [
            Rule("read", "ha.read", "entity:*", "allow"),
            Rule("write", "ha.write", "entity:*", "require_approval"),
        ]
    )
    assert policy.evaluate("ha.read", "entity:light.kitchen")["decision"] == "allow"
    assert policy.evaluate("ha.delete", "entity:light.kitchen")["decision"] == "deny"


def test_approval_is_scoped_and_single_use() -> None:
    policy = Policy([Rule("write", "ha.write", "entity:*", "require_approval")])
    approval = policy.issue_approval(
        "run-1", "ha.write", "entity:light.kitchen", ttl=timedelta(minutes=1)
    )
    assert (
        policy.evaluate("ha.write", "entity:light.kitchen", run_id="run-1", approval_id=approval)[
            "decision"
        ]
        == "allow"
    )
    assert (
        policy.evaluate("ha.write", "entity:light.kitchen", run_id="run-1", approval_id=approval)[
            "decision"
        ]
        == "require_approval"
    )
    assert (
        policy.evaluate("ha.write", "entity:light.bedroom", run_id="run-1", approval_id=approval)[
            "decision"
        ]
        == "require_approval"
    )


def test_decisions_are_traced_without_approval_token(tmp_path: Path) -> None:
    trace = TraceStore(tmp_path / "trace.sqlite3")
    run_id = trace.start_run()["run_id"]
    policy = Policy([Rule("write", "ha.write", "entity:*", "require_approval")])
    result = policy.evaluate("ha.write", "entity:light.kitchen", run_id=run_id, trace=trace)
    assert result["decision"] == "require_approval"
    assert "approval" not in trace.inspect(run_id)["events"][-1]["payload"]
