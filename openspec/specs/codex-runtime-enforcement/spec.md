# Codex Runtime Enforcement Specification

## Purpose

This capability connects the repository's agent-platform controls to Codex lifecycle hooks so tool calls, subagents, approvals, recovery, and completion evidence are enforced at the Codex boundary.

## Requirements

### Requirement: The runtime SHALL establish a traced Codex session
At session start, the runtime MUST create or resume a run identifier, record repository revision and context-pack identity when available, and expose the run identifier to later hooks. A session without a usable trace boundary MUST fail closed for controlled operations.

#### Scenario: Start a controlled session
- **WHEN** Codex starts a repository session with a valid workspace
- **THEN** the runtime creates a traced run and records session provenance before controlled tool use

#### Scenario: Trace initialization fails
- **WHEN** the runtime cannot initialize the trace boundary
- **THEN** controlled tool operations are blocked and the failure is reported without executing them

### Requirement: The runtime SHALL enforce policy before controlled tool use
Before a controlled tool executes, the runtime MUST evaluate its operation and resource through the existing policy boundary. `deny` and `require_approval` MUST prevent execution; an allowed operation MUST receive a trace decision event.

#### Scenario: Denied tool call
- **WHEN** a Codex tool call has no matching allow rule
- **THEN** the hook blocks the call and records a redacted denial

#### Scenario: Approval-required tool call
- **WHEN** a tool call requires approval without a valid approval bound to the run and scope
- **THEN** the hook pauses or blocks the call and does not execute it

### Requirement: The runtime SHALL trace tool, subagent, and handoff lifecycle
The runtime MUST record tool start/result or failure, subagent start/stop, parent-child relationships, and handoff evidence references. Hook payloads MUST be redacted before persistence.

#### Scenario: Delegate to a specialist
- **WHEN** Codex starts a subagent
- **THEN** the runtime records a child run and the requested specialist scope

#### Scenario: Tool failure
- **WHEN** a controlled tool fails
- **THEN** the runtime records the failure classification and applies the reliability policy before any retry

### Requirement: The runtime SHALL enforce completion evidence
At stop, the runtime MUST verify trace integrity, required evaluation/governance evidence, and unresolved approval state. It MUST block or mark the run incomplete when required evidence is absent and MUST never equate automated pass with product-owner acceptance.

#### Scenario: Complete controlled run
- **WHEN** trace, evaluations, governance checks, and handoffs are valid
- **THEN** the runtime records a successful terminal state with evidence references

#### Scenario: Incomplete controlled run
- **WHEN** required evidence or integrity verification is missing
- **THEN** the runtime records an incomplete outcome and prevents a clean completion claim

### Requirement: The runtime SHALL expose its enforcement limits
The runtime documentation MUST state which Codex hooks, tools, and harness surfaces it controls, how hooks become trusted, and which external actions remain outside its control.

#### Scenario: Review enforcement coverage
- **WHEN** an operator inspects the runtime configuration
- **THEN** the controlled events, fail-closed behavior, trust requirement, and bypass limitations are explicit
