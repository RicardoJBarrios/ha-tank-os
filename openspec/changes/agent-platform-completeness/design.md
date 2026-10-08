# Design

## Context

The runtime currently blocks `require_approval` during `PreToolUse`, which
prevents Codex from reaching its native `PermissionRequest` event. The native
hook JSON only has a POSIX command, while CI supports Windows. The repository
contains native hooks and optional plugin packaging, but ownership and language
checks do not yet enforce the intended boundary.

## Goals / Non-Goals

**Goals:**

- Preserve the provider-neutral policy decision as `require_approval`.
- Add a `PermissionRequest` recorder that declines to decide, leaving the
  normal Codex prompt in control.
- Keep deny/block behavior for unknown or explicitly denied tools.
- Add `command_windows` alongside the POSIX hook command and test both shapes.
- Add CODEOWNERS for the setup surfaces and a coherence check for active
  configuration.
- Establish an English technical-documentation boundary without translating
  the product vision in this change.

**Non-Goals:**

- Product PRD, SRD, architecture, ADRs, database, or Home Assistant feature
  implementation.
- Automatic approval, bypassing Codex permissions, or broadening HA access.
- Committing, pushing, or changing GitHub remote protection.

## Decisions

1. **Use `PermissionRequest` as a recorder, not an approver.** Codex supports a
   hook that can allow, deny, or decline to decide. The project returns no
   decision for `require_approval`, allowing the normal host prompt to continue.
   Alternatives considered: blocking in `PreToolUse` (safe but unusable for
   implementation) and auto-allowing (rejected because it violates policy).

2. **Keep one native enforcement source.** `.codex/hooks.json` remains active;
   plugin files remain distribution artifacts only. The self-test and health
   command validate that `.codex/config.toml` disables the local plugin.

3. **Use Codex's `command_windows` field.** The same Python launcher remains
   the implementation, with `py -3` as the Windows interpreter command. This
   follows Codex's platform-specific hook configuration rather than relying on
   shell aliases.

4. **Add ownership without changing product authority.** CODEOWNERS covers
   setup and integration paths; it does not assign product acceptance or
   replace the product owner's authority.

5. **Use a technical documentation allowlist.** The existing Spanish product
   vision remains untouched. New and maintained platform documentation is
   English, and the tooling checks target the agent-platform document set.

## Risks / Trade-offs

- [Risk] A Codex surface may not emit `PermissionRequest` → the self-test
  exercises the event contract, and real-client validation remains required.
- [Risk] Windows has a different Python installation → `py -3` is explicit and
  the health report identifies missing interpreter configuration.
- [Risk] CODEOWNERS can slow reviews → ownership is limited to high-impact
  setup paths and can be revised through a normal pull request.

## Migration Plan

1. Extend the runtime and tests with permission-request handling.
2. Add Windows commands and update self-tests and documentation.
3. Add ownership and coherence checks.
4. Run the full quality gate and direct hook probes on the current host. No
   external migration is needed and no commit/push is performed.
