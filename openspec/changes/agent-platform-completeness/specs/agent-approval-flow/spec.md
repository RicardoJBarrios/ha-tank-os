# Spec Delta

## Purpose

This capability lets Codex retain control of approval prompts while ensuring
the repository policy never silently authorizes a write, shell, or other
approval-required operation.

## ADDED Requirements

### Requirement: Approval-required operations SHALL defer to the host

The project hook SHALL record a `require_approval` policy decision and defer to
Codex's native approval lifecycle. It SHALL block denied or unknown operations
and SHALL never convert `require_approval` into an automatic approval.

#### Scenario: Shell operation requires approval

- **WHEN** a shell operation matches a `require_approval` policy rule
- **THEN** the pre-tool hook does not deny it solely because approval is
  required, and Codex's native approval flow remains responsible for the final
  decision

#### Scenario: Unknown operation is denied

- **WHEN** a tool is not present in the controlled registry while strict mode
  is active
- **THEN** the hook denies the operation before execution

#### Scenario: Host approval is recorded

- **WHEN** Codex emits a permission request for an approval-required operation
- **THEN** the runtime records the redacted request and does not auto-approve it
