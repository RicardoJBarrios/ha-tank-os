# Tasks

## 1. Approval lifecycle

- [x] 1.1 Add `PermissionRequest` handling that records redacted requests and defers approval; verify runtime tests cover allow, require-approval, and deny cases
- [x] 1.2 Change strict pre-tool behavior so require-approval remains non-executable by the adapter but is not denied before the host prompt; verify unknown and denied tools remain blocked
- [x] 1.3 Add the PermissionRequest hook and document the host-mediated approval flow; verify self-test coverage and docs are aligned

## 2. Cross-platform enforcement

- [x] 2.1 Add Windows hook commands for every lifecycle event and verify the native hook JSON includes both launchers
- [x] 2.2 Extend self-test and health diagnostics for platform launcher coverage; verify the checks fail on malformed configuration

## 3. Governance and coherence

- [x] 3.1 Add CODEOWNERS for agent platform, CI/security, Home Assistant, and documentation paths; verify the file is included in quality checks
- [x] 3.2 Add configuration coherence checks and remove or clearly mark duplicate active hook packaging; verify native hooks remain canonical
- [x] 3.3 Align technical setup documentation with the English-language rule and verify spelling/language checks
- [x] 3.4 Replace the misleading Spec Kit template with an explicit not-adopted status and verify authority documentation is unambiguous

## 4. Integration verification

- [x] 4.1 Run the full quality and security gate, OpenSpec validation, and diff checks; verify no product files or remote Git state were changed
- [x] 4.2 Exercise the permission and strict-block hook contracts with direct payloads and document the remaining client-surface validation boundary
