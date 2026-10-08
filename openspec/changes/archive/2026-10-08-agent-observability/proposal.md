# Proposal

## Why

Trace records explain individual executions, but operators also need aggregated health signals to detect failures, latency growth, retries, stalled runs, and tool errors without reading every event. Local observability should derive from the trace and remain useful offline.

## What Changes

- Add a provider-neutral local observability capability derived from agent trace events.
- Provide deterministic counters, duration summaries, failure and stale-run counts, and tool/error breakdowns.
- Support a machine-readable snapshot and a human-readable report with explicit time windows and data limits.
- Keep metrics local and avoid external telemetry, product data, or automatic actuation.

## Capabilities

### New Capabilities

- `agent-observability`: Local derived metrics and health reports for agent executions.

### Modified Capabilities

None.

## Impact

- Adds a read-only aggregation layer and CLI/report documentation over the trace store.
- Adds tests for empty windows, incomplete runs, failures, durations, and deterministic output.
- Does not change Home Assistant behavior or send data to external systems.
