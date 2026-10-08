# Design

## Context

The runtime currently persists one `codex-session.json` path per repository,
while hook payloads can arrive from multiple Codex sessions. Native hooks are
the active enforcement surface, but the repository also contains plugin hook
packaging and POSIX-only command substitution. Local Home Assistant MCP and
SonarQube are useful dependencies with different readiness requirements.

## Goals / Non-Goals

**Goals:**

- Derive a deterministic state path from a validated session identity.
- Keep the existing provider-neutral trace, policy, reliability, and evidence
  modules as the implementation authority.
- Make the native hook commands work from the repository root without relying
  on shell-specific environment assignment or command substitution.
- Provide one redacted health command suitable for local preflight and CI
  diagnostics.
- Keep host approval as the execution boundary for operations classified as
  `require_approval`; the runtime records the request but never grants it by
  itself.

**Non-Goals:**

- Product implementation, persistence design, or Home Assistant control
  behavior.
- A SonarQube MCP integration. The scanner/API remains canonical.
- Automatic installation, startup, or repair of external services.

## Decisions

1. **Session-keyed state files.** Use a sanitized hash of the payload session
   identity under `.agent-state/sessions/`, with a small compatibility path for
   test fixtures that explicitly inject `STATE_FILE`. A hash avoids path
   traversal and keeps session identifiers out of filenames. Alternatives
   considered: one global file (rejected because it races) and in-memory state
   (rejected because each hook is a separate process).

2. **Native hooks are canonical.** Keep `.codex/hooks.json` as the only active
   project enforcement source. The plugin package remains distributable but is
   disabled in `.codex/config.toml` and checked by health diagnostics. This
   avoids deleting a package that may be useful to another Codex client while
   preventing two active copies in this repository.

3. **Python launcher with explicit repository root.** Hook commands invoke the
   checked-in Python entry point through a small launcher that receives the
   repository root from Codex's session working directory. The launcher uses
   `git rev-parse` through Python's subprocess API and passes the root directly
   to the runtime, avoiding shell command substitution and inline environment
   assignment. Alternatives considered: POSIX shell syntax (rejected for
   Windows) and separate hand-maintained shell scripts (rejected as duplicate
   logic).

4. **Health is diagnostic, not repair.** `pnpm agent:health` performs local
   checks, redacts secrets, and returns non-zero only for required checks. It
   does not start Docker, mutate Home Assistant, or change Codex trust. This
   makes failures observable and safe to run before strict mode.

5. **Approval remains host-mediated.** The adapter returns an explicit
   `require_approval` result to its internal policy layer and never converts it
   to `allow` in strict mode. Native Codex permission handling remains the
   authority for the actual approval prompt; the adapter records the policy
   decision and blocks unsupported direct execution paths.

## Risks / Trade-offs

- [Risk] A client may omit a session identifier → strict mode fails closed with
  a remediation message; audit mode remains useful for payload discovery.
- [Risk] Old test fixtures expect one state path → retain injectable state
  paths for tests and migrate repository fixtures to explicit identities.
- [Risk] Local service checks can fail on an intentionally stopped service →
  report actionable `unavailable` status and distinguish it from a malformed
  configuration.
- [Risk] Plugin-capable clients may need the package → preserve the package,
  but require an explicit mode change before enabling it alongside native hooks.

## Migration Plan

1. Add session-keyed state and migrate runtime tests and self-test fixtures.
2. Add the portable launcher and update native hook commands.
3. Add health diagnostics, package script, tests, and documentation.
4. Run the self-test, Python tests, quality gate, and a real Codex audit and
   strict probe. Rollback is a revert of this bounded change; no external data
   migration is required.

## Open Questions

None. Product baseline and product persistence decisions remain outside this
environment-hardening change.
