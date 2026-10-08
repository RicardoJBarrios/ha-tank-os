# Spec Delta

## Purpose

This capability provides a provider-neutral, local record of agent execution so that runs, delegated work, context, tools, and resulting evidence can be reconstructed and verified without making product data the trace authority.

## ADDED Requirements

### Requirement: The system SHALL identify and lifecycle-track every agent run

Each run record MUST have a stable run identifier, a lifecycle status, creation and completion timestamps, and enough metadata to identify its initiating agent, provider/model, repository revision, OpenSpec change, and task when those values are available. A delegated run MUST reference its parent run.

#### Scenario: Start a top-level run
- **WHEN** an agent execution starts with repository and task context
- **THEN** the system creates a uniquely identifiable run with status `running` and records the available provenance metadata

#### Scenario: Start a delegated run
- **WHEN** an agent delegates work to another agent
- **THEN** the child run records the parent run identifier and remains independently queryable

#### Scenario: Finish a run
- **WHEN** a run completes successfully, fails, is cancelled, or is abandoned
- **THEN** the system records exactly one terminal status with a completion timestamp and preserves the reason or error classification when available

### Requirement: The system SHALL record ordered append-only run events

Events MUST belong to a run, have a stable event identifier, a monotonically increasing sequence within that run, an event type, an occurrence timestamp, and a redacted payload. Once accepted, an event MUST NOT be silently overwritten or reordered.

#### Scenario: Append a valid event
- **WHEN** a caller appends an event for an existing non-terminal run with the next sequence number
- **THEN** the event is persisted and can be read in sequence order

#### Scenario: Reject an invalid append
- **WHEN** a caller submits an event with a duplicate identifier, an invalid sequence, or a terminal run
- **THEN** the system rejects the append without changing the existing event history

### Requirement: The system SHALL make trace history tamper-evident

Each event MUST commit to the previous event's integrity value and its canonical event content. Verification MUST detect missing, duplicated, reordered, or modified events and MUST report the affected run and sequence.

#### Scenario: Verify an intact run
- **WHEN** a caller verifies a run whose stored events are unchanged
- **THEN** verification succeeds and reports the event count and terminal status

#### Scenario: Detect altered history
- **WHEN** an event payload, sequence, predecessor reference, or integrity value is changed
- **THEN** verification fails and identifies the first inconsistent event when it can be determined

### Requirement: The system SHALL link runs to reproducibility context and evidence

A run MUST support references to the exact repository revision, context-pack identity or cache key, agent/skill versions, tool-call records, and produced artifacts or evidence. References MUST distinguish metadata from content and MUST remain valid when the referenced item is unavailable.

#### Scenario: Reconstruct run inputs
- **WHEN** a caller requests a run summary
- **THEN** the summary includes its provenance references and states which references are missing, stale, or unavailable

#### Scenario: Link an artifact
- **WHEN** an agent produces a file, report, decision, or test result
- **THEN** the run can record an artifact reference with type, locator, creation event, and verification status without copying the artifact content into the trace by default

### Requirement: The system SHALL protect trace storage from secret disclosure

Before persistence or export, the system MUST redact configured secret patterns, authentication tokens, credentials, and sensitive headers from event payloads and tool-call inputs/outputs. The trace MUST record that redaction occurred without retaining the original secret.

#### Scenario: Redact a sensitive value
- **WHEN** an event contains a configured token or credential pattern
- **THEN** the persisted event contains a stable redaction marker and no recoverable original value

#### Scenario: Export a trace
- **WHEN** a caller exports a run
- **THEN** the export applies the same redaction boundary and includes a schema version and export timestamp

### Requirement: The system SHALL support local inspection, export, and incomplete-run recovery

The local trace interface MUST support querying a run and its events, exporting a portable redacted representation, verifying integrity, and marking stale non-terminal runs as abandoned only through an explicit recovery operation. Recovery MUST preserve the original events and record the recovery reason.

#### Scenario: Inspect a run
- **WHEN** a caller requests a known run identifier
- **THEN** the system returns its lifecycle, provenance, ordered events, references, and integrity status

#### Scenario: Recover a stale run
- **WHEN** an operator explicitly recovers a run that has exceeded the configured stale threshold without a terminal event
- **THEN** the system marks it `abandoned`, records the recovery event and reason, and does not delete prior evidence

#### Scenario: Query an unknown run
- **WHEN** a caller requests an identifier that does not exist
- **THEN** the interface returns a clear not-found result without creating or modifying trace data
