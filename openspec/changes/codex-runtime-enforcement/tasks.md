# Tasks

## 1. Codex adapter foundation

- [x] 1.1 Define the plugin-compatible hook configuration, strict/audit modes, controlled-tool registry, and self-test fixtures; verify configuration is valid and unknown events are reported.
- [x] 1.2 Implement session start/resume, run-id propagation, provenance/context-pack capture, and redaction; verify initialization failure blocks controlled operations.

## 2. Enforcement hooks

- [x] 2.1 Implement PreToolUse policy and approval enforcement; verify allow, deny, require-approval, malformed-payload, and unknown-tool cases.
- [x] 2.2 Implement PostToolUse and Stop trace/evidence validation; verify tool failures, incomplete evidence, and clean completion outcomes.
- [x] 2.3 Implement SubagentStart/SubagentStop parent-child and handoff recording; verify specialist scope and failed handoff cases.

## 3. Integration and operations

- [x] 3.1 Connect reliability, evaluation, governance, and lineage modules without duplicating their logic; verify an end-to-end controlled run fixture.
- [x] 3.2 Add Codex installation, trust, audit-to-strict activation, diagnostics, and rollback documentation; verify the documented self-test runs locally.
- [x] 3.3 Run full tests, quality, security, context, OpenSpec, pre-commit, and diff validation; record harness-specific limitations.
