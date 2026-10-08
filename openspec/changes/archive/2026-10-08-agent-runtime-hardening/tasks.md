# Tasks

## 1. Session isolation

- [x] 1.1 Implement session-keyed runtime state with safe identity hashing and verify concurrent session tests pass
- [x] 1.2 Preserve parent/child trace correlation and verify subagent lifecycle tests pass
- [x] 1.3 Update the Codex self-test and runtime documentation to require an explicit session identity and verify the documented command succeeds

## 2. Hook portability and source governance

- [x] 2.1 Add the cross-platform repository-root launcher and update native hook commands; verify JSON configuration and launcher tests pass
- [x] 2.2 Add a duplicate-source diagnostic and verify native hooks remain the only active project enforcement source
- [x] 2.3 Document host-mediated approval behavior and verify strict mode never turns `require_approval` into an internal allow

## 3. Environment health

- [x] 3.1 Implement redacted health checks for hooks, runtime registry, Home Assistant MCP, and optional SonarQube; verify required and optional failure cases
- [x] 3.2 Add `pnpm agent:health` and document remediation without automatic service mutation; verify the command exits with the documented statuses

## 4. Integration verification

- [x] 4.1 Run the Codex self-test, Python tests, formatting, linting, OpenSpec validation, and diff checks; record results in the change evidence
- [x] 4.2 Exercise the trusted native hooks with a real Codex audit and strict probe, verifying clean stop behavior and policy blocking
