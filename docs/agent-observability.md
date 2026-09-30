# Agent Observability

Observability is a read-only derived view over the local agent trace. It produces bounded JSON metrics for an explicit UTC window and never returns event payloads.

```bash
pnpm agent:observability -- \
  --start 2026-01-01T00:00:00Z \
  --end 2027-01-01T00:00:00Z \
  --max-rows 10000
```

The result includes the source trace schema/store, window, coverage and truncation status, run counts by status, event-type counts, and valid duration summaries. An empty window returns zero-valued metrics. A bounded or malformed source is reported rather than treated as complete.

This is local development observability. It does not send telemetry, create alerts, actuate Home Assistant, or replace canonical project evidence.
