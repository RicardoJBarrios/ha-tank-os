# Repository-Governance Specification

## Purpose

This capability keeps agent-platform ownership, language policy, and active
configuration sources explicit so the repository remains maintainable as the
product team grows.

## Requirements

### Requirement: Protected areas SHALL have declared ownership

The repository SHALL declare review ownership for runtime, agent instructions,
hooks, CI, security configuration, and Home Assistant integration surfaces.

#### Scenario: Protected file has an owner

- **WHEN** a pull request changes a protected agent-platform path
- **THEN** GitHub can request review from the declared owner

### Requirement: The active enforcement source SHALL be unambiguous

The repository SHALL identify native project hooks as the active enforcement
source and SHALL fail its coherence check if a second project source is
enabled unintentionally.

#### Scenario: Plugin packaging remains optional

- **WHEN** plugin packaging is retained for distribution
- **THEN** it is clearly marked optional and does not become an active second
  enforcement source

### Requirement: Versioned technical documentation SHALL be English

The agent-platform documentation and configuration guidance SHALL be written
in English, while preserving product-language requirements as product scope.

#### Scenario: Tooling documentation is audited

- **WHEN** the repository documentation language check runs
- **THEN** it reports no Spanish setup or agent-tooling document as the
  canonical technical guide
