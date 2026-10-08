# Agent-Permissions-And-Approvals Specification

## Purpose

This capability makes agent tool access explicit, bounded, and auditable by evaluating every operation against configured rules and requiring approval for sensitive actions.

## Requirements

### Requirement: The system SHALL evaluate every operation against explicit policy

An operation decision MUST include the operation name, resource scope, decision, policy version, and reason. Unknown operations or scopes MUST be denied unless an explicit matching rule exists.

#### Scenario: Allow a matching operation
- **WHEN** an operation matches an explicit allow rule
- **THEN** the evaluator returns `allow` with the rule and policy version

#### Scenario: Deny an unknown operation
- **WHEN** an operation has no matching rule
- **THEN** the evaluator returns `deny` and identifies the missing authorization

### Requirement: The system SHALL require explicit approval for sensitive operations

Rules MUST support `require_approval`. An approval MUST be bound to the operation, scope, run, policy version, and expiration; an approval for another scope or expired approval MUST NOT authorize execution.

#### Scenario: Sensitive operation awaits approval
- **WHEN** a matching rule requires approval and no valid approval exists
- **THEN** the evaluator returns `require_approval` without executing the operation

#### Scenario: Approval is consumed
- **WHEN** a valid single-use approval matches the requested operation and scope
- **THEN** the evaluator returns `allow` and marks the approval as consumed

### Requirement: The system SHALL make policy decisions auditable

When a run identifier is supplied, every decision MUST be recorded as a redacted trace event containing the operation, scope, decision, rule identifier, policy version, and reason. Secrets or approval tokens MUST NOT be stored.

#### Scenario: Record a denied decision
- **WHEN** a policy evaluation denies an operation for a traced run
- **THEN** the trace contains a redacted decision event and the operation is not executed

#### Scenario: Policy changes are distinguishable
- **WHEN** the policy version changes
- **THEN** subsequent decisions identify the new version and are not conflated with prior decisions
