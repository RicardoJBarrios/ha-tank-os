# Spec Delta

## Purpose

This capability turns local agent execution traces into bounded, reproducible health reports so operators can detect reliability and performance problems without inspecting every run manually.

## ADDED Requirements

### Requirement: The system SHALL derive bounded execution metrics from trace data

For an explicit time window, the system MUST report run counts by status, completed-run duration summaries, event counts, failure counts, and incomplete-run counts. It MUST identify the window and source trace schema in every result.

#### Scenario: Report a populated window
- **WHEN** an operator requests metrics for a window containing successful, failed, and running runs
- **THEN** the report contains deterministic counts and duration summaries for exactly that window

#### Scenario: Report an empty window
- **WHEN** an operator requests a window with no trace records
- **THEN** the report returns zero-valued metrics with the requested window and no fabricated health claims

### Requirement: The system SHALL expose actionable failure and latency breakdowns

Reports MUST include failure classifications when available, tool/event type counts, and duration percentiles or clearly labeled unavailable values. Aggregations MUST not expose redacted payload content.

#### Scenario: Inspect failure sources
- **WHEN** failed runs and tool error events exist in the window
- **THEN** the report groups them by status/reason and event type without returning secret-bearing payloads

### Requirement: The system SHALL make derived reports reproducible and bounded

The interface MUST accept explicit start/end timestamps or a documented default, include generation time and source database identity, and support a maximum row/event scan bound. Truncation MUST be visible in the result.

#### Scenario: Enforce a scan bound
- **WHEN** the source contains more records than the configured maximum
- **THEN** the report indicates truncation and does not imply complete coverage

#### Scenario: Generate machine-readable output
- **WHEN** an operator requests JSON output
- **THEN** the output has stable field names, schema version, and no raw event payloads
