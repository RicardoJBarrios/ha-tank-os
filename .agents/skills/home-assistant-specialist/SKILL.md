---
name: home-assistant-specialist
description: Design, implement, and verify Home Assistant Core and custom integrations, entities, config entries, APIs, frontend boundaries, automation interfaces, compatibility, security, tests, and the local MCP target. Use for all Home Assistant-specific technical work.
---

# Home Assistant specialist

Act as the repository specialist for the complete Home Assistant platform
surface used by this repository: Core architecture, custom integrations,
devices and entities, config entries, frontend/API boundaries, automation and
service interfaces, testing, compatibility, operations, security, and the
local development target. This skill is technical guidance, not a source of
product requirements or global architectural authority.

## Required context

Read `AGENTS.md`, `docs/vision-y-requisitos.md`,
`docs/metodologia-modelado-sdd.md`, `docs/agent-tooling.md`, and
`docs/home-assistant-compatibility.md` before changing code or configuration.
Read the active approved OpenSpec change and relevant BMAD architecture and
ADRs when they exist. Do not work around `Product baseline ready` or `Change
ready` gates.

## Scope and practices

### Platform architecture

- Model Home Assistant through its event bus, state machine, service registry,
  timers, config-entry lifecycle, device/entity registries, areas, repairs,
  diagnostics, recorder boundaries, and frontend data flow.
- Prefer the smallest native capability that satisfies the approved behavior.
  Do not create a custom integration, custom entity domain, service, panel, or
  persistence layer when an existing Home Assistant abstraction is sufficient.
- Keep Home Assistant state and Recorder as integration surfaces, not an
  automatic product source of truth. Define ownership, provenance, retention,
  and synchronization explicitly.

### Integrations and config entries

- For custom integrations, validate `manifest.json`, domain ownership,
  dependencies, version support, translations, brands, and the selected
  integration quality-scale target before implementation.
- Prefer UI config flows and unique config entries. Implement connection
  validation before setup, reauthentication and reconfiguration where needed,
  migration for schema changes, and unloading that removes listeners,
  entities, tasks, and connections cleanly.
- Store per-entry runtime state in `ConfigEntry.runtime_data`; avoid mutable
  module globals and duplicate setup. Use a `DataUpdateCoordinator` for shared
  polling or push-to-entity coordination when appropriate.
- Model devices and entities with stable unique IDs, correct device classes,
  state classes, units, entity categories, availability, translation keys,
  disabled-by-default decisions, and lifecycle ownership.

### Runtime, APIs, and frontend

- Keep the event loop non-blocking. Use async APIs and injected web sessions;
  never perform blocking network, filesystem, subprocess, or CPU-heavy work on
  the event loop without an explicit safe boundary.
- Handle timeouts, retries, rate limits, offline state, authentication
  failures, cancellation, backoff, and recovery deliberately. Log actionable
  transitions without filling logs or exposing secrets.
- Treat REST and WebSocket APIs as integration contracts. Validate payloads,
  schema, permissions, subscriptions, reconnect behavior, and error handling.
  Keep frontend code aligned with Home Assistant's unidirectional data flow,
  accessible UI contracts, and stable API boundaries; do not assume internal
  frontend modules are public APIs.
- Register services/actions with validation, translation-aware descriptions,
  explicit response semantics, and config-entry ownership. Separate read-only
  observation from any action that can control equipment.

### Quality, localization, and security

- Use the Home Assistant Integration Quality Scale as a roadmap: Bronze is the
  minimum baseline for a new Core integration, while Silver, Gold, and Platinum
  add resilience, diagnostics, translations, coverage, strict typing,
  asynchronous design, and efficiency requirements. Record the chosen target
  and exceptions rather than claiming a tier prematurely.
- Treat user input, network responses, URLs, tokens, diagnostics, logs,
  service data, and imported configuration as untrusted. Apply least privilege,
  redact sensitive values, avoid unsafe dynamic evaluation, and never access
  production devices from the test environment.
- Keep product language, locale, timezone, location, and metric-unit
  preferences distinct. Use Home Assistant translation and unit conventions
  where applicable; do not hard-code display strings, units, or regional
  assumptions in domain logic.

### Testing and operations

- Test setup, config flow, unique-entry behavior, authentication failures,
  reauth, migration, unload, entities, registries, services, events,
  availability, recovery, and representative API/WebSocket behavior.
- Use deterministic pytest fixtures for fast behavior tests and the isolated
  container for black-box HTTP/WebSocket/configuration lifecycle checks. Keep
  startup, MCP handshake, import success, compatibility, and product
  acceptance as separate gates.
- Keep the local target disposable: use the pinned `compose.ha.yaml` service,
  bind it to localhost, and never use real credentials, devices, or production
  state.

### MCP as one development interface

- The local MCP endpoint is
  `http://127.0.0.1:8123/api/mcp/assist`; read `HA_TEST_TOKEN` from the user
  environment only. Never write or print the token.
- Use MCP for agent-facing inspection and explicitly authorized control against
  the disposable local instance. Prefer REST, WebSocket, and pytest as the
  canonical executable test interfaces.
- MCP transport readiness is not proof of integration compatibility, entity
  correctness, frontend behavior, or product acceptance.

Use `uv run pytest` and the repository test scripts for executable evidence.
Keep Python and container Home Assistant versions aligned unless the change
records the reason for divergence.

## Boundaries and reporting

Do not modify canonical product requirements, create parallel specifications,
push to `main`, or claim compatibility from a running container alone. Report
files changed, exact commands, versions, passed/failed/skipped checks, and
remaining product-owner validation separately.
