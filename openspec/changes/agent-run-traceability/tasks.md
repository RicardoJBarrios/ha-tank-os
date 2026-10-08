# Tasks

## 1. Store and schema foundation

- [x] 1.1 Define versioned run, event, tool-call, artifact-reference, and export schemas with migrations and uniqueness constraints; verify schema creation and migration tests pass on a temporary database.
- [x] 1.2 Add configurable local operational-store paths and ignored-state defaults without changing product persistence; verify a clean checkout does not require the store to exist.
- [x] 1.3 Implement canonical event serialization, per-run sequencing, predecessor references, and tamper-evident digests; verify deterministic serialization and chain verification tests pass.

## 2. Run lifecycle and event recording

- [x] 2.1 Implement start-run and delegated-child-run operations with provenance fields and lifecycle validation; verify top-level and parent-child lifecycle tests pass.
- [x] 2.2 Implement append-event and terminal-run operations with transactional ordering and rejection of invalid appends; verify duplicate, out-of-order, and terminal-run tests pass.
- [x] 2.3 Implement integrity verification and actionable failure reporting for modified, missing, duplicated, and reordered events; verify corruption-fixture tests identify the first inconsistent sequence.

## 3. Redaction and provenance

- [x] 3.1 Implement pre-persistence and pre-export redaction for configured credentials, tokens, sensitive headers, and secret environment values; verify representative secret fixtures never appear in stored or exported content.
- [x] 3.2 Integrate repository revision, context-pack identity/cache key, resolver version, agent/skill versions, and tool-call metadata as structured references; verify a run summary reports unavailable references explicitly.
- [x] 3.3 Implement artifact and evidence references with locator, type, digest when available, creation event, and verification status; verify references remain queryable when the target is missing.

## 4. Local operations and recovery

- [x] 4.1 Implement inspect and redacted export operations with schema version, export timestamp, lifecycle data, ordered events, references, and integrity status; verify export round-trip tests pass without embedding source files by default.
- [x] 4.2 Implement explicit stale-run recovery that appends a recovery event and preserves prior history; verify stale, fresh, terminal, and unknown-run cases.
- [x] 4.3 Add bounded transactional concurrency handling and deterministic busy/error behavior; verify concurrent append tests pass within the documented local limit.
- [x] 4.4 Document the local trace interface, storage boundary, redaction guarantees, recovery procedure, retention handoff, and failure limits in English; verify every documented command is runnable in a temporary store.

## 5. Integration and delivery evidence

- [x] 5.1 Integrate one agent execution path with run start, event recording, terminal status, and context-pack provenance without changing product behavior; verify an end-to-end trace fixture is complete and integrity-valid.
- [x] 5.2 Add regression coverage for provider-neutral event envelopes and schema-version compatibility; verify the Python and repository quality suites pass.
- [x] 5.3 Run context validation, OpenSpec validation, repository quality checks, and `git diff --check`; record commands, versions, results, and known limits in the change evidence.
