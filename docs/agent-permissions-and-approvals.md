# Agent Permissions and Approvals

Agent operations must pass through an explicit policy boundary. The evaluator returns `allow`, `deny`, or `require_approval`; unknown operations are denied. A broad local Home Assistant MCP rule is therefore a deliberate configuration decision, not an implicit capability.

Rules are matched by exact operation and resource pattern. Approval records are scoped to a run and operation, expire, and can be consumed once. Approval identifiers and secrets are never written to the trace; the decision metadata is recorded as a redacted `policy.decision` event.

Example:

```python
from agent_platform.policy import Policy, Rule

policy = Policy(
    [
        Rule("ha-read", "ha.read", "entity:*", "allow"),
        Rule("ha-write", "ha.write", "entity:*", "require_approval"),
    ]
)
```

The policy module is an adapter boundary. Tool integrations must evaluate before execution and must not treat an approval-required result as permission to proceed.
