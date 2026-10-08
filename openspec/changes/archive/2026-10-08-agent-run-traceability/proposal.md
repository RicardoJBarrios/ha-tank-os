# Proposal

## Why

Agent work currently leaves execution evidence scattered across chat history, terminal output, and generated files. That makes it difficult to reconstruct what an agent did, which context and tool versions it used, whether a run completed, and which artifacts or decisions resulted from it. A provider-neutral local trace is needed before observability, permissions, evaluation, and evidence-lineage controls can be made reliable.

## What Changes

- Introduce a local traceability capability for agent runs and their lifecycle events.
- Assign stable identifiers to runs and events, including parent-run relationships for delegated work.
- Record reproducibility metadata such as repository revision, OpenSpec change/task, agent and skill identities, model/provider information, and context-pack identity.
- Store ordered, append-only events with tamper-evident chaining and explicit lifecycle states.
- Record references to tool calls, artifacts, evidence, and redacted inputs/outputs without making product data or Home Assistant Recorder the trace authority.
- Provide local inspection, export, integrity verification, and incomplete-run recovery operations.
- Keep the operational trace local and excluded from version control by default; define retention and redaction hooks for the later privacy control.

## Capabilities

### New Capabilities

- `agent-run-traceability`: Provider-neutral local recording and verification of agent execution runs, events, provenance, and related evidence references.

### Modified Capabilities

None.

## Impact

- Adds an agent-platform operational store and a small local command/API surface for creating, appending, querying, exporting, and verifying traces.
- Integrates with the existing context resolver so a run can reference the exact context-pack cache key and source revision used at a task boundary.
- Adds tests, configuration, and documentation for lifecycle states, redaction boundaries, integrity checks, and incomplete-run handling.
- Does not add product persistence, Home Assistant entities, Home Assistant Recorder data, external telemetry, permission enforcement, dashboards, or model/provider routing.
