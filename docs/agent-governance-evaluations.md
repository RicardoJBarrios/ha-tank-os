# Agent Governance Evaluations

The governance suite evaluates eleven independent controls:

1. Documentary authority.
2. Obsolete specifications.
3. Contradictions.
4. Context-pack use.
5. Secret exposure.
6. Specialist delegation.
7. Protection of `main`.
8. Code quality.
9. Test coverage.
10. Handoff correctness.
11. Recovery from failed tools.

The evaluator is fail-closed: missing evidence is a failure, not a pass. It does not collect evidence or mutate the repository; adapters must supply evidence from the context resolver, trace, Git, CI, quality tools, and handoff records.

```python
from agent_platform.governance import CHECKS, evaluate_governance

evidence = {check.evidence_key: True for check in CHECKS}
report = evaluate_governance(evidence, run_id="run-id")
```

An automated pass remains `product_owner_validation: pending`. The suite is a governance gate and evidence summary, not product acceptance.
