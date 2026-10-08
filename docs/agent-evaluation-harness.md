# Agent Evaluation Harness

The local evaluator checks structured agent results without invoking an agent or tool. Cases are versioned and can require markers, forbid markers, require a status, and enforce a latency limit.

```python
from agent_platform.evaluation import EvaluationCase, evaluate

result = evaluate(
    EvaluationCase("ha-smoke", "1", required_markers=("safe",)),
    status="succeeded",
    summary="safe result",
    duration_seconds=0.4,
)
```

Evidence is bounded and redacted. An automated `pass` never means product acceptance: `product_owner_validation` remains `pending` until the product owner validates it separately.
