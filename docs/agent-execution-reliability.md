# Agent Execution Reliability

The reliability policy is a decision layer. It never executes or retries an operation itself.

An adapter must provide the failure class, current attempt, idempotency declaration, deadline, and cancellation state. Only transient failures of explicitly idempotent operations can produce `retry`. Permanent, unsafe, cancelled, timed-out, and exhausted executions produce terminal decisions.

```python
from agent_platform.reliability import FailureClass, ReliabilityPolicy

decision = ReliabilityPolicy(max_attempts=3).decide(
    FailureClass.TRANSIENT,
    attempt=1,
    idempotent=True,
)
```

The returned delay is bounded and deterministic. Adapters must record the decision in the execution trace before scheduling a retry.
