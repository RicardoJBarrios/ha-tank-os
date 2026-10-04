# Validation Evidence

## Storage and lifecycle spike

| Item | Result |
| --- | --- |
| Host Python | 3.14.6 on macOS 26.6.2 arm64 |
| Test Python environment | Python 3.14.6 |
| Home Assistant package | 2026.9.4 |
| Home Assistant container | Pinned image digest from `compose.ha.yaml`, running on Linux |
| Container readiness | `pnpm ha:up`, `pnpm ha:wait`, and `pnpm ha:status` passed; status correctly reported authentication required |
| Native persistence primitive | `homeassistant.helpers.storage.Store` with `atomic_writes=True` |
| Versioning | Store major/minor version metadata is persisted and a migration callback receives the prior version and data |
| Atomic write evidence | A successful save was reloaded from `.storage/tank_os.foundation`; a simulated atomic-write failure left the previous canonical file unchanged in the contract test |
| Migration evidence | A version `1.1` payload was migrated to version `2.1` and rewritten with the migrated data in an isolated probe |

## Decision for this change

Use Home Assistant `Store` as the storage adapter primitive behind the ha-tank-os repository boundary. The adapter enables atomic file replacement, versioned major/minor metadata, and migration callbacks. The application repository rereads the saved payload and raises a persistence error when the committed data cannot be confirmed.

This decision applies to the first product slice and is not a claim that all future data volumes or telemetry workloads should use the same mechanism. High-volume telemetry remains outside this change.

## Native Home Assistant surface evidence

- The integration exposes a normal Home Assistant config flow without declaring `single_config_entry` in the manifest.
- Multiple Tanks are represented inside the canonical repository; the integration configuration is not the Tank model.
- Native services provide structured responses for Tank/context creation and retrieval and route mutations through the application service.
- Contract tests verify that a Home Assistant user context is required for mutations and that no custom frontend is needed for the first context workflow.

## Limits

- The tested Home Assistant version is the repository's pinned development line, not a declared product compatibility range.
- The black-box container proves lifecycle availability only; it does not authenticate a product user or prove the integration behavior.
- Backup restoration, multi-process concurrency, and high-volume telemetry retention are not validated by this spike.

## Implementation verification

- `pnpm test:python`: 48 tests passed.
- `pnpm lint:markdown`: passed.
- `pnpm lint:planning`: passed with 0 issues.
- `pnpm lint:spelling`: passed.
- `pnpm lint:python`: passed.
- `pnpm format:python:check`: passed.
- `pnpm typecheck:python`: passed with mypy 1.18.2.
- `pnpm lint:frontend`: passed.
- `pnpm format:frontend:check`: passed.
- `pnpm audit --audit-level=high`: no known vulnerabilities.
- Python security scan: no issues identified.
- OpenSpec validation: 13 changes passed.
- Product baseline readiness: ready.
- `git diff --check`: passed.

The implementation review found no discrepancy requiring an update to the
approved PRD, capability map, architecture spine, or this change's
specifications. Product-owner validation remains separate from these technical
results.
