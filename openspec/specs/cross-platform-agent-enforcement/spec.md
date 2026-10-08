# Cross-Platform-Agent-Enforcement Specification

## Purpose

This capability makes the repository's agent enforcement executable and
verifiable across the supported macOS, Linux, and Windows development hosts.

## Requirements

### Requirement: Hooks SHALL define supported platform launchers

The native hook configuration SHALL provide a valid launcher for POSIX hosts
and Windows hosts for every enforced lifecycle event.

#### Scenario: POSIX launcher resolves the repository

- **WHEN** a hook runs from the repository or a nested working directory on a
  POSIX host
- **THEN** it resolves the Git root and invokes the runtime in strict mode

#### Scenario: Windows launcher is configured

- **WHEN** the hook configuration is inspected on Windows
- **THEN** every enforced event has a Windows command and the self-test reports
  the platform configuration as valid
