# Home Assistant Compatibility

The product targets Home Assistant, but no integration manifest or product
Python source exists yet. Compatibility is therefore a pending engineering
baseline, not an already verified version claim.

## Current policy

- Follow the currently supported Home Assistant development Python version
  once the integration shape is approved. The current Home Assistant developer
  documentation requires Python 3.14.2 or newer for its development
  environment.
- Keep the repository Python floor at 3.14.2 through [`.python-version`](../.python-version)
  and CI until the product baseline adopts a different supported floor.
- Use Home Assistant's native integration scaffolding and validation rules when
  the product baseline confirms a custom integration. Do not invent a parallel
  Home Assistant runtime or entity model.
- Add a compatibility job that installs the selected Home Assistant release and
  runs the integration tests as soon as `custom_components/**/manifest.json`
  exists.
- Use the local black-box target in `compose.ha.yaml` for API, config-flow,
  entity, restart, and migration scenarios that cannot be proven by Python
  tests alone. Keep these tests opt-in and isolated from production instances.
- Use the `test` extra in `pyproject.toml` for deterministic Python integration
  tests. The current development pin is Home Assistant `2026.9.4` with
  `pytest-homeassistant-custom-component` `0.13.367`.
- Record the tested Home Assistant version, Python version, platform, and test
  result. A local successful import is not evidence of compatibility with all
  supported Home Assistant releases.

## Pending baseline decisions

- Whether the first deliverable is a custom integration or a contribution to
  Home Assistant Core.
- The integration domain and manifest ownership.
- The minimum and maximum supported Home Assistant release range.
- The test strategy for config flow, storage, translations, entities, and
  migration behavior.

## Local test target

The repository provides two complementary test layers:

1. Python tests run through `uv` for fast, deterministic integration behavior.
2. A pinned Home Assistant Container for black-box HTTP, WebSocket, lifecycle,
   and configuration verification.

The layers are intentionally separate. The container's readiness endpoint does
not authenticate a user, load product code, or validate product behavior. The
standalone container exposes MCP only after the official MCP Server integration
is configured. This development instance uses that integration with the
built-in Assist API at `/api/mcp/assist`. HTTP/WebSocket and pytest remain the
canonical test interfaces; MCP is an additional agent-facing interface and
requires the user-owned `HA_TEST_TOKEN`.

The official Home Assistant developer documentation covers [environment
setup](https://developers.home-assistant.io/docs/development_environment/),
[integration scaffolding](https://developers.home-assistant.io/docs/creating_component_index/),
and [testing](https://developers.home-assistant.io/docs/development_testing/).
