# Codex Runtime Enforcement

This repository provides a Codex-compatible hook adapter under `.codex-plugin/`. It connects Codex lifecycle events to the existing provider-neutral agent platform without duplicating trace, policy, reliability, evaluation, governance, or lineage logic.

## Modes

The adapter defaults to `audit` when invoked directly. The repository's native
Codex hooks run it in `strict` mode after the real Codex hook contract has been
verified:

```bash
CODEX_RUNTIME_MODE=audit pnpm agent:codex:self-test
```

Audit mode records decisions and unknown events but does not block them. The
project enforcement entry point is `.codex/hooks.json`; it sets
`CODEX_RUNTIME_MODE=strict` for every native Codex hook invocation. Direct
strict-mode verification can be run with:

```bash
CODEX_RUNTIME_MODE=strict codex
```

Strict mode blocks unknown tools, denied operations, missing trace initialization,
and incomplete stop evidence. Approval-required operations are recorded and
deferred to Codex's native approval flow; the project adapter never grants the
approval itself.

## Installation and trust

The root `plugin.json` is the canonical portable package and points to the
root `hooks/hooks.json` for optional distribution. The `.codex-plugin/` files
remain compatibility artifacts only. They are not active in this repository:
`.codex/hooks.json` is the canonical enforcement surface and
`.codex/config.toml` explicitly disables the project plugin to prevent
duplicate execution. Review and explicitly trust the project hook definition
before relying on it. An untrusted hook is not an enforcement boundary.

Run the repository self-test before enabling strict mode:

```bash
pnpm agent:codex:self-test
```

After changing `.codex/hooks.json`, review and trust the new hook hash in the
Codex `/hooks` interface again. Codex deliberately requires trust for the
current project hook contents; a previous trust decision does not authorize a
changed hook definition.

The self-test verifies repository hook coverage and the controlled-tool registry. It does not prove that every Codex client emits identical payloads; that requires a real audit-mode session for each client surface.

## Controlled lifecycle

- `SessionStart`: creates or resumes the trace boundary.
- `PreToolUse`: evaluates the controlled-tool registry and policy.
- `PermissionRequest`: records an approval request and defers to the Codex host.
- `PostToolUse`: records redacted outcomes.
- `SubagentStart` / `SubagentStop`: records parent-child and handoff lifecycle.
- `Stop`: validates trace and governance evidence before clean completion.

The adapter is fail-closed only in strict mode. Commands run outside Codex,
untrusted or disabled hooks, unsupported harness events, and direct access to
tools not routed through this adapter remain outside its control. GitHub branch
protection and CI are independent backstops. `pnpm agent:health` checks the
native hook source and local Home Assistant MCP without printing the token;
SonarQube is optional and is checked only when `SONAR_HOST_URL` is configured.

Runtime state is isolated by the Codex session identity. A missing identity is
accepted only for `SessionStart`; subsequent strict events fail closed because
they cannot be correlated safely. Repository writes and shell operations remain
`require_approval`: the runtime records the policy decision but never grants
that approval itself. The host's native approval boundary is still required.
