"""Tests for safe execution decisions."""

from datetime import UTC, datetime, timedelta

from agent_platform.reliability import FailureClass, ReliabilityPolicy


def test_retries_only_transient_idempotent_failures() -> None:
    policy = ReliabilityPolicy(max_attempts=3, base_delay=1)
    assert policy.decide(FailureClass.TRANSIENT, attempt=1, idempotent=True)["decision"] == "retry"
    assert (
        policy.decide(FailureClass.PERMANENT, attempt=1, idempotent=True)["decision"] == "terminal"
    )
    assert (
        policy.decide(FailureClass.TRANSIENT, attempt=1, idempotent=False)["decision"] == "terminal"
    )


def test_bounds_deadline_attempts_and_cancellation() -> None:
    now = datetime.now(UTC)
    policy = ReliabilityPolicy(max_attempts=2, deadline=now + timedelta(seconds=1))
    assert (
        policy.decide(FailureClass.TRANSIENT, attempt=2, idempotent=True, now=now)["reason"]
        == "maximum attempts reached"
    )
    assert (
        policy.decide(
            FailureClass.TRANSIENT, attempt=1, idempotent=True, now=now + timedelta(seconds=2)
        )["decision"]
        == "timed_out"
    )
    assert (
        policy.decide(FailureClass.TRANSIENT, attempt=1, idempotent=True, now=now, cancelled=True)[
            "decision"
        ]
        == "cancelled"
    )
