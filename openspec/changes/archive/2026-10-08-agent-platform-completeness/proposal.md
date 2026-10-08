# Proposal

## Why

The development platform is usable on the primary machine, but several
guardrails are incomplete: strict hooks block approval-required work before
Codex can ask for approval, Windows hook execution is not configured, and the
repository still permits ownership and documentation drift. These gaps should
be closed before product implementation starts.

## What Changes

- Route approval-required operations through Codex's native approval lifecycle
  without granting approval in the project policy adapter.
- Add Windows hook commands and platform-specific self-tests.
- Make the active hook and plugin packaging boundaries unambiguous and detect
  drift between optional distribution files and the native project hook.
- Add CODEOWNERS and repository governance checks for protected areas.
- Complete the English-language tooling documentation and remove stale setup
  wording without changing product requirements.
- Add regression tests and quality checks for the corrected behavior.

## Capabilities

### New Capabilities

- `agent-approval-flow`: Defers approval-required operations to the Codex host
  while preserving policy decisions and trace evidence.
- `cross-platform-agent-enforcement`: Runs and validates the agent hooks on
  macOS, Linux, and Windows.
- `repository-governance`: Declares ownership and detects configuration drift
  in the agent-platform surface.

### Modified Capabilities

## Impact

The change affects the Codex runtime adapter, native hook configuration, agent
self-tests, package scripts, repository governance files, and environment
documentation. It intentionally does not create product requirements,
architecture decisions, a PRD, or product implementation.
