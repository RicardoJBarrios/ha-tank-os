# Home Assistant Compatibility

The product currently uses a custom Home Assistant integration in
`custom_components/tank_os/`. Compatibility remains a pending engineering
baseline: the repository pins a test version but has not declared a supported
Home Assistant release range.

## Current policy

- Follow the currently supported Home Assistant development Python version
  once the integration shape is approved. The current Home Assistant developer
  documentation requires Python 3.14.2 or newer for its development
  environment.
- Keep the repository Python floor at 3.14.2 through [`.python-version`](../.python-version)
  and CI until the product baseline adopts a different supported floor.
- Use Home Assistant's native integration scaffolding and validation rules.
  Do not invent a parallel Home Assistant runtime or entity model.
- Add compatibility jobs for the declared supported Home Assistant releases
  when the support range is selected.
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

- The minimum and maximum supported Home Assistant release range.
- The Home Assistant Integration Quality Scale target.
- Additional compatibility coverage beyond the currently pinned integration
  test environment.

## Local test target

### Test execution platforms

`pnpm test:python` runs portable repository tests on Windows, Linux, and macOS.
The pinned Home Assistant pytest plugin imports the POSIX-only `fcntl` module,
so the runner disables that plugin on native Windows before test collection.
Tests that start or import the Home Assistant runtime must explicitly report
Windows skips and defer those imports until after the platform check. Linux
and macOS CI keep the plugin enabled and run the complete runtime test suite.

A passing Windows tooling check is not evidence of native Windows Home
Assistant runtime support. Contributors on Windows use the Linux container
target for Home Assistant execution. The required Windows quality job still
runs Python tests and the remaining quality checks; it is not a static-only
replacement for testing.

### Complementary test layers

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
