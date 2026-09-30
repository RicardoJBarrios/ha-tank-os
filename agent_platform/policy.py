"""Explicit local authorization policy for agent operations."""

from __future__ import annotations

import fnmatch
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

from .trace import TraceStore

Decision = Literal["allow", "deny", "require_approval"]


@dataclass(frozen=True)
class Rule:
    rule_id: str
    operation: str
    resource: str
    decision: Decision


@dataclass
class Approval:
    approval_id: str
    run_id: str
    operation: str
    resource: str
    expires_at: datetime
    consumed: bool = False


class Policy:
    """Deny-by-default evaluator with scoped single-use approvals."""

    def __init__(self, rules: list[Rule], *, version: str = "1") -> None:
        self.rules = tuple(rules)
        self.version = version
        self._approvals: dict[str, Approval] = {}

    def issue_approval(
        self, run_id: str, operation: str, resource: str, *, ttl: timedelta = timedelta(minutes=10)
    ) -> str:
        approval_id = str(uuid.uuid4())
        self._approvals[approval_id] = Approval(
            approval_id, run_id, operation, resource, datetime.now(UTC) + ttl
        )
        return approval_id

    def evaluate(
        self,
        operation: str,
        resource: str,
        *,
        run_id: str | None = None,
        approval_id: str | None = None,
        trace: TraceStore | None = None,
    ) -> dict[str, str]:
        matches = [
            rule
            for rule in self.rules
            if rule.operation == operation and fnmatch.fnmatchcase(resource, rule.resource)
        ]
        rule = next((item for item in matches if item.decision == "deny"), None) or next(
            iter(matches), None
        )
        decision: Decision = "deny" if rule is None else rule.decision
        reason = "no matching rule" if rule is None else f"matched rule {rule.rule_id}"
        if rule and rule.decision == "require_approval":
            approval = self._approvals.get(approval_id or "")
            valid = (
                approval
                and not approval.consumed
                and approval.run_id == run_id
                and approval.operation == operation
                and fnmatch.fnmatchcase(resource, approval.resource)
                and approval.expires_at > datetime.now(UTC)
            )
            if valid:
                approval.consumed = True
                decision = "allow"
                reason = f"approval accepted for rule {rule.rule_id}"
            else:
                decision = "require_approval"
                reason = f"approval required by rule {rule.rule_id}"
        result = {
            "decision": decision,
            "operation": operation,
            "resource": resource,
            "policy_version": self.version,
            "reason": reason,
        }
        if trace and run_id:
            trace.append_event(run_id, "policy.decision", result)
        return result
