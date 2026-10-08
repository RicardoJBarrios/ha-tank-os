# Spec Delta

## Purpose

This capability limits local agent operational data, makes sensitivity visible, and provides a recoverable decision boundary before any trace cleanup occurs.

## ADDED Requirements

### Requirement: The system SHALL classify agent data by retention boundary

Data MUST be classified as operational trace, derived evaluation evidence, canonical project authority, or product/runtime data. Retention operations MUST only target explicitly selected agent-platform classes.

#### Scenario: Classify a trace
- **WHEN** a local trace is evaluated for retention
- **THEN** it is identified as operational trace and is eligible only under the configured trace policy

#### Scenario: Protect canonical data
- **WHEN** a purge is requested
- **THEN** canonical documents and product/runtime data are outside the selectable target set

### Requirement: The system SHALL require explicit and reviewable retention actions

Retention policies MUST define a cutoff, target class, and dry-run behavior. Dry-run MUST be the default and MUST report candidate counts without deletion.

#### Scenario: Preview retention
- **WHEN** an operator runs retention without an explicit destructive confirmation
- **THEN** the system reports candidates and performs no deletion

#### Scenario: Purge selected traces
- **WHEN** an operator explicitly confirms a trace purge
- **THEN** only matching trace records are deleted and the operation reports the cutoff, count, and policy version

### Requirement: The system SHALL preserve privacy guarantees

Retention reports and audit events MUST not expose original secrets, approval tokens, or unbounded payloads. Purge operations MUST be idempotent.

#### Scenario: Repeat a purge
- **WHEN** the same confirmed purge is run twice
- **THEN** the second operation reports zero additional candidates and does not affect other data
