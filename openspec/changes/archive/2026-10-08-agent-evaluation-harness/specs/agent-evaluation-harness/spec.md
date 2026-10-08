# Spec Delta

## Purpose

This capability provides repeatable, versioned checks for agent execution results and produces evidence that distinguishes automated evaluation from product-owner acceptance.

## ADDED Requirements

### Requirement: The system SHALL evaluate versioned cases deterministically

Each case MUST have an identifier, version, input metadata, expected status, required markers, forbidden markers, and optional latency limit. Evaluation MUST return the case identity and all checks.

#### Scenario: Passing case
- **WHEN** an execution result matches status and marker constraints
- **THEN** the evaluator returns pass with every check recorded

#### Scenario: Failing case
- **WHEN** a result misses a required marker or contains a forbidden marker
- **THEN** the evaluator returns fail with actionable failed checks

### Requirement: The system SHALL produce bounded evaluation evidence

Evidence MUST include evaluator schema, case identity/version, execution reference when available, result status, checks, timestamp, and duration. It MUST NOT include secrets or unbounded raw transcripts.

#### Scenario: Export evaluation evidence
- **WHEN** an evaluation is completed
- **THEN** its JSON evidence is portable, redacted, and sufficient to reproduce the checks

### Requirement: The system SHALL distinguish automation from acceptance

Automated pass MUST NOT be represented as product acceptance. Reports MUST expose an explicit `product_owner_validation` state that is pending until supplied externally.

#### Scenario: Automated pass remains pending acceptance
- **WHEN** all automated checks pass
- **THEN** the report says pass while product-owner validation remains pending
