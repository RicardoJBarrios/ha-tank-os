# Proposal

## Why

Agent changes need repeatable checks for correctness, safety, and regression detection. Chat review alone cannot provide comparable evidence across prompts, models, skills, and tool versions.

## What Changes

- Add a local evaluation harness with versioned cases and deterministic result summaries.
- Support expected status, required output markers, forbidden markers, and latency limits.
- Produce machine-readable evaluation evidence linked to a trace run.

## Capabilities

### New Capabilities

- `agent-evaluation-harness`: Repeatable local evaluation cases and evidence summaries for agent executions.

### Modified Capabilities

None.

## Impact

- Adds a provider-neutral evaluator and tests.
- Does not decide product acceptance or replace human review.
