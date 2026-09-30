---
name: ha-test-environment
description: Operate the repository's isolated Home Assistant test environment and Python integration-test harness.
---

# Home Assistant Test Environment

Use this skill when starting, inspecting, stopping, or testing the repository's
local Home Assistant container, or when preparing tests for a future custom
integration.

## Required context

Read `AGENTS.md`, `docs/agent-tooling.md`, and
`docs/home-assistant-compatibility.md` before changing the test environment or
declaring compatibility.

## Operating rules

- Use the repository package scripts; do not invoke an unpinned global HA
  command.
- The container is a disposable local test target. It must bind only to
  `127.0.0.1`, must not use host networking, privileged mode, host devices, or
  real aquarium data.
- Never commit `.storage`, databases, logs, secrets, access tokens, or test
  user credentials. The local onboarding user and tokens belong to the operator.
- The project-local Codex MCP server uses `HA_TEST_TOKEN` and the configured
  `/api/mcp/assist` endpoint. Verify that the token exists outside the
  repository before using MCP tools; never replace it with a committed value.
- Mount `custom_components/` read-only. Product code belongs in the approved
  change, not in the environment scaffold.
- Use `requirements-dev.txt` and `uv` for the Python test environment. Keep
  the Python package version aligned with the container version unless a test
  explicitly documents why it cannot be aligned.
- A passing container startup proves availability only. It does not prove
  integration compatibility, behavior, or product acceptance.
- MCP availability proves transport and authentication only. It does not
  authorize destructive operations or replace explicit product tests.

## Canonical commands

```sh
pnpm ha:up
pnpm ha:wait
pnpm ha:status
pnpm ha:mcp:status
uv sync --extra test
uv run pytest
pnpm ha:logs
pnpm ha:down
```

For a clean local state, stop the service and remove only the repository's
`.docker/ha/config/.storage` and database files after confirming that no useful
test evidence is stored there. Do not remove Docker volumes or unrelated
containers from this skill.

## Reporting

Report the Home Assistant image digest, Python package version, Python version,
Docker platform, exact test command, and whether the result is technical
verification or product-owner validation. Record unsupported or untested HA
release ranges explicitly.
