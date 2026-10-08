# Agent-Artifact-And-Evidence-Lineage Specification

## Purpose

This capability makes agent-produced artifacts and evidence traceable to their run, sources, content digest, and verification state without duplicating canonical content.

## Requirements

### Requirement: The system SHALL create complete lineage manifests

Each manifest MUST include a stable artifact identifier, artifact type, locator, producer run when available, source references, content digest when readable, creation time, and verification state.

#### Scenario: Register an artifact
- **WHEN** an agent produces a report or test result
- **THEN** the manifest records its provenance and digest without copying its content

### Requirement: The system SHALL verify artifact integrity

Verification MUST recompute a readable artifact digest and report missing, changed, or verified states. It MUST never claim verified for an unavailable locator.

#### Scenario: Verify unchanged artifact
- **WHEN** the locator exists and its digest matches
- **THEN** verification returns `verified`

#### Scenario: Detect changed artifact
- **WHEN** the locator exists but its digest differs
- **THEN** verification returns `changed`

### Requirement: The system SHALL distinguish derived evidence from authority

Manifests MUST label artifacts as derived and retain source references. A manifest MUST NOT promote an artifact to canonical product or requirement authority.

#### Scenario: Handoff evidence
- **WHEN** a manifest is exported for a handoff
- **THEN** its derived status and source references remain visible
