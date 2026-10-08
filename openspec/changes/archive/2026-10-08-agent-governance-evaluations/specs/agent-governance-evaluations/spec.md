# Spec Delta

## Purpose

This capability evaluates whether agent work respected repository authorities, security and Git safeguards, specialist delegation, engineering quality, handoffs, and recovery evidence.

## ADDED Requirements

### Requirement: The system SHALL evaluate the complete governance checklist

The suite MUST expose independent checks for documentary authority, obsolete specifications, contradictions, context-pack use, secret exposure, specialist delegation, main-branch protection, code quality, test coverage, handoffs, and tool-failure recovery. The checklist contains eleven controls and MUST report each one independently.

#### Scenario: Complete evidence set
- **WHEN** all eleven evidence predicates are true
- **THEN** the suite returns pass with eleven named passing checks

#### Scenario: Missing evidence
- **WHEN** one or more predicates are absent or false
- **THEN** the suite returns fail or incomplete for those checks and never assumes success

### Requirement: The system SHALL preserve evidence provenance and limitations

Each check MUST identify its evidence key and result. The report MUST state that automated checks are not product-owner acceptance and MUST include unresolved or unavailable evidence explicitly.

#### Scenario: Review a failed control
- **WHEN** a governance check fails
- **THEN** the report identifies the control, evidence key, and remediation-relevant detail

### Requirement: The system SHALL remain non-mutating

Running the governance suite MUST not modify `main`, product data, canonical specifications, or Home Assistant state.

#### Scenario: Run the suite
- **WHEN** governance evaluation executes against supplied evidence
- **THEN** it returns a report without changing repository or runtime state
