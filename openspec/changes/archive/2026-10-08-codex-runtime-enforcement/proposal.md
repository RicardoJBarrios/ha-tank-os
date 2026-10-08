# Proposal

## Why

The repository already defines traceability, permissions, reliability, evaluation, privacy, and evidence-lineage controls, but ordinary Codex runs can still bypass them unless they are connected to Codex's lifecycle. This change establishes the Codex-specific enforcement boundary so those controls are executed at tool, subagent, and session lifecycle points.

## What Changes

- Add a local Codex plugin/runtime package with trusted lifecycle hooks.
- Create a run at session start and maintain provenance through tool calls and subagent handoffs.
- Evaluate tool operations through the existing policy boundary before execution.
- Record tool outcomes, reliability decisions, evaluations, and lineage references through the existing platform modules.
- Block or pause disallowed and approval-required operations at the Codex hook boundary.
- Validate final stop conditions and fail closed when required evidence is missing.
- Document Codex-specific limits: hooks require trust and only control events exposed by the selected Codex harness.

## Capabilities

### New Capabilities

- `codex-runtime-enforcement`: Codex lifecycle hooks and a local enforcement runtime that connects agent-platform controls to Codex execution.

### Modified Capabilities

None.

## Impact

- Adds Codex hook configuration, local hook scripts, runtime adapters, tests, and operational documentation.
- Uses existing `agent_platform` modules; it does not duplicate trace, policy, reliability, evaluation, or lineage implementations.
- Does not change Home Assistant product behavior or grant access to the non-disposable HA environment.
