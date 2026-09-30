# Proposal

## Why

The current Codex runtime proves the policy and trace concepts, but it is not
safe for concurrent sessions and its operational dependencies are not visible
through one health check. The native hook path also contains platform-specific
shell syntax and duplicated packaging sources, which can produce inconsistent
enforcement across clients.

## What Changes

- Isolate runtime state by Codex session and preserve parent/child run
  correlation.
- Add a repository health check for Codex hooks, local Home Assistant MCP,
  optional local SonarQube, and duplicate enforcement sources.
- Make native hook launching portable and keep one canonical active hook source.
- Add explicit handling and documentation for host-mediated approvals so
  `require_approval` is never silently treated as execution permission.
- Extend runtime tests and setup documentation with real-client and failure
  recovery checks.

## Capabilities

### New Capabilities

- `agent-runtime-health`: Detects whether the agent runtime and its local
  dependencies are ready before strict operation.
- `agent-session-isolation`: Keeps trace and policy state isolated across
  concurrent Codex sessions.

### Modified Capabilities

## Impact

The change affects `agent_platform/codex_runtime.py`, Codex hook configuration,
runtime scripts, tests, setup documentation, and package scripts. It does not
implement product functionality or require a new external service.
