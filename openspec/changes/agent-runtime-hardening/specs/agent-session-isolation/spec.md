# Spec Delta

## Purpose

This capability prevents concurrent or nested agent sessions from sharing
mutable runtime state, while preserving traceability between parent and child
runs.

## ADDED Requirements

### Requirement: Session state SHALL be isolated

The runtime SHALL store and load lifecycle state using a stable session
identity supplied by the hook payload, and SHALL NOT use one repository-wide
state file for all sessions.

#### Scenario: Concurrent sessions remain independent

- **WHEN** two sessions receive `SessionStart` events with different session
  identities
- **THEN** each session gets a different state record and subsequent tool
  events are appended only to that session's run

#### Scenario: Missing identity fails closed in strict mode

- **WHEN** a non-`SessionStart` event has no usable session identity and strict
  mode is enabled
- **THEN** the runtime blocks the event and records that session correlation is
  unavailable

### Requirement: Child runs SHALL retain parent correlation

The runtime SHALL associate a `SubagentStart` run with the current session's
parent run and SHALL keep the session identity in the child state.

#### Scenario: Subagent trace is correlated

- **WHEN** a subagent starts inside an initialized session
- **THEN** the returned child run has the current run as its parent and remains
  addressable through the same session state
