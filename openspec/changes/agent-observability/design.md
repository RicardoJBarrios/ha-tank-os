# Design

## Context

The trace store from `agent-run-traceability` is the sole input. Observability is a derived view and must not become another source of truth.

## Goals / Non-Goals

**Goals:** deterministic local snapshots, bounded scans, useful reliability and latency summaries, and safe machine-readable output.

**Non-Goals:** external telemetry, dashboards, alert delivery, product metrics, cost accounting, or automatic remediation.

## Decisions

Implement a read-only aggregator over SQLite using explicit UTC windows. Use standard-library calculations for counts and percentile ranks to avoid a new runtime dependency. Do not include event payloads; aggregate event types and safe status/reason values only. Report incomplete and truncated data explicitly.

The CLI will expose an observability snapshot operation and the Python API will accept a trace store, start/end timestamps, and maximum scanned rows. Output schema is versioned independently from trace storage.

## Risks / Trade-offs

- [Risk] Local clocks or malformed timestamps affect duration data. → Mitigation: label invalid/unavailable durations and keep counts separate.
- [Risk] A bounded scan can hide older failures. → Mitigation: include truncation metadata and require explicit windows for evidence.
- [Risk] Aggregated reason fields may contain sensitive text. → Mitigation: reuse trace redaction and restrict classification to bounded normalized values.

## Migration Plan

Add the read-only aggregator and tests; no migration is required. If the trace schema is unavailable, return a clear operational error rather than creating product data.

## Open Questions

None.
