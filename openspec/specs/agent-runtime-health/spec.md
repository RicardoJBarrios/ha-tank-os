# Agent-Runtime-Health Specification

## Purpose

This capability provides one deterministic, redacted readiness report for the
Codex enforcement surface and the local services that agents are authorized to
use.

## Requirements

### Requirement: Runtime health SHALL be explicit and redacted

The health command SHALL report independent checks for hook configuration,
controlled tools, session isolation, Home Assistant MCP, and SonarQube when
configured. It SHALL never print credentials or token values.

#### Scenario: Ready local environment

- **WHEN** the hooks are valid and configured local services respond
- **THEN** the command exits successfully and reports each check as `pass`

#### Scenario: Optional SonarQube is unavailable

- **WHEN** SonarQube is not configured or not running
- **THEN** the command marks SonarQube as `not_configured` or `unavailable`,
  explains the remediation, and does not claim the service is healthy

#### Scenario: Required Home Assistant MCP is unavailable

- **WHEN** the configured Home Assistant MCP endpoint cannot complete its
  initialize handshake
- **THEN** the command exits unsuccessfully, reports the endpoint failure
  without exposing the token, and strict readiness is not granted

### Requirement: Active enforcement SHALL have one canonical source

The repository SHALL identify one active native hook configuration. Optional
plugin packaging MAY remain available for distribution, but it SHALL be
disabled or clearly marked as non-active when native project hooks are used.

#### Scenario: Duplicate active sources are detected

- **WHEN** native hooks and plugin hooks are both enabled for the repository
- **THEN** the health command fails and identifies the duplicate source

#### Scenario: Native hooks are trusted

- **WHEN** the configured project hooks are trusted by the Codex client
- **THEN** the health report confirms native enforcement and identifies the
  required trust action if the client has not trusted them
