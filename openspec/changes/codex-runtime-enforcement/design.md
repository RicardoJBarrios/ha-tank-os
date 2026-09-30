# Design

## Context

The repository has provider-neutral trace, policy, reliability, evaluation, governance, retention, observability, and lineage modules. Codex supports lifecycle hooks and plugin-bundled hooks, but hook behavior depends on the selected Codex harness and trusted installation state.

## Goals / Non-Goals

**Goals:** connect Codex lifecycle events to existing controls, fail closed for controlled tool calls, preserve one trace boundary, and make limits visible.

**Non-Goals:** replace Codex, intercept arbitrary processes outside Codex, control every possible future harness event, or change product/Home Assistant persistence.

## Decisions

### Codex plugin plus repository hooks

Use a local plugin-compatible layout with `hooks/hooks.json` and scripts under a repository-owned runtime directory. Keep the provider-specific adapter thin: it parses Codex hook input, calls provider-neutral Python modules, and emits Codex-compatible allow/block/context decisions. This avoids duplicating platform policy.

### Fail closed at PreToolUse and validate at Stop

`PreToolUse` is the enforcement point for policy and approval. `PostToolUse` records outcomes and links artifacts. `SubagentStart` and `SubagentStop` handle delegation. `Stop` verifies completion evidence. Session initialization creates the run and context identity.

### Explicit controlled-tool registry

The runtime will maintain an allowlisted mapping from Codex tool names to policy operation/resource extraction. Unknown tools are logged as uncontrolled and blocked when the configured mode is strict. This avoids pretending that arbitrary provider payloads are equivalent.

### Trust and harness compatibility

Hook installation and trust are explicit prerequisites. The runtime reports its active mode and hook coverage. Codex CLI, IDE, and plugin surfaces must be tested separately because compatible hook files do not guarantee identical payloads or event semantics.

### Alternatives considered

- **Instructions only:** rejected because they cannot enforce a tool decision.
- **MCP gateway only:** insufficient because Codex built-in tools can bypass an MCP-only gateway.
- **Custom external agent loop:** offers stronger control but would stop using Codex as the primary harness; retain as a future option if hook enforcement proves insufficient.

## Risks / Trade-offs

- [Risk] A Codex surface may not emit an expected hook event. → Mitigation: fail closed for strict operations, expose coverage diagnostics, and test CLI/IDE separately.
- [Risk] Hook scripts are untrusted or unavailable. → Mitigation: installation verification and explicit trust documentation; no claims of enforcement until a self-test passes.
- [Risk] Tool schemas change. → Mitigation: version the adapter, reject unknown payloads in strict mode, and retain raw payloads only after redaction.
- [Risk] A user can run commands outside Codex. → Mitigation: GitHub branch protection and CI remain independent backstops; document the boundary honestly.

## Migration Plan

1. Add hook schema, runtime adapter, and self-test fixtures.
2. Run Codex in audit mode to discover actual tool payloads without blocking.
3. Enable strict mode for the repository after hook trust and coverage self-tests pass.
4. Route the local HA MCP through the guarded tool registry.
5. Roll back by disabling the plugin hooks; CI and repository protections remain active.

## Open Questions

None that change the contract. Exact Codex payload fields must be confirmed by runtime self-tests before strict activation.
