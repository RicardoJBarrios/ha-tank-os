# Proposal

## Why

Local agent access must be explicit and auditable even when the development MCP has broad capability. Without a policy boundary, a tool can be invoked without a stable decision, scope, or approval record.

## What Changes

- Add a provider-neutral policy evaluator for agent operations.
- Support explicit allow, deny, and approval-required decisions by operation and resource scope.
- Default unknown operations to denial and prevent approval bypasses.
- Record policy decisions in the local trace when a run is supplied.

## Capabilities

### New Capabilities

- `agent-permissions-and-approvals`: Explicit local authorization decisions and auditable approval handling for agent operations.

### Modified Capabilities

None.

## Impact

- Adds a small policy module and tests; no external identity provider is required.
- Existing Home Assistant local access remains configurable, but broad access must be represented by an explicit policy rule.
- Product behavior and Home Assistant Recorder are unchanged.
