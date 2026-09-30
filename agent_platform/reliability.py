"""Deterministic safety policy for retrying agent operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class FailureClass(StrEnum):
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


@dataclass(frozen=True)
class ReliabilityPolicy:
    max_attempts: int = 3
    base_delay: float = 0.5
    max_delay: float = 30.0
    deadline: datetime | None = None

    def decide(
        self,
        failure: FailureClass,
        *,
        attempt: int,
        idempotent: bool,
        now: datetime | None = None,
        cancelled: bool = False,
    ) -> dict[str, object]:
        """Return a retry decision without executing the operation."""
        current = now or datetime.now(UTC)
        if cancelled or failure == FailureClass.CANCELLED:
            return self._result("cancelled", attempt, "execution cancelled")
        if self.deadline and current >= self.deadline:
            return self._result("timed_out", attempt, "execution deadline exceeded")
        if failure != FailureClass.TRANSIENT or not idempotent:
            return self._result("terminal", attempt, "failure is not safely retryable")
        if attempt >= self.max_attempts:
            return self._result("terminal", attempt, "maximum attempts reached")
        delay = min(self.max_delay, self.base_delay * (2 ** max(0, attempt - 1)))
        return self._result("retry", attempt + 1, "transient idempotent failure", delay)

    @staticmethod
    def _result(decision: str, attempt: int, reason: str, delay: float = 0.0) -> dict[str, object]:
        return {"decision": decision, "attempt": attempt, "delay_seconds": delay, "reason": reason}
