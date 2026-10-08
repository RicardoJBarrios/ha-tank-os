# Proposal

## Why

The generic evaluation harness does not yet prove the engineering and governance behaviors required from agents. A dedicated suite is needed to check authority, context use, security, delegation, Git discipline, quality, handoffs, and recovery.

## What Changes

- Add explicit governance checks for every control in the agreed checklist.
- Treat missing evidence as a failed or incomplete check rather than assuming success.
- Produce a versioned summary that distinguishes automated results from human acceptance.
- Document the source evidence and limitations for each check.

## Capabilities

### New Capabilities

- `agent-governance-evaluations`: Automated governance evaluation cases for agent behavior and delivery evidence.

### Modified Capabilities

None.

## Impact

- Extends the local evaluation package and adds a deterministic test suite.
- Connects conceptually to context, trace, quality, Git, and handoff evidence without mutating those systems.
