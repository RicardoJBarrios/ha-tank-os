# Validation Evidence

**Change:** `associate-ha-sources-with-native-history`

**Date:** 2026-10-08

**Evidence type:** Technical verification; this is not product-owner acceptance of the implementation.

## Environment

- Home Assistant: `2026.9.4` (repository test pin)
- Python: `3.14.6`
- `pytest-homeassistant-custom-component`: `0.13.367`
- Host: macOS, Apple Silicon (`aarch64-apple-darwin`)
- Node.js: `v24.18.0`; pnpm: `11.17.0`

## Results

- `pnpm quality:checks` — passed. Python suite: 53 tests; braces suite: 2 tests; Markdown/planning/spelling lint, Ruff, formatting, mypy, ESLint, Prettier, security checks, OpenSpec validation, product readiness, and tracked-file diff checks passed.
- `pnpm exec openspec validate --all` — 15 artifacts passed, 0 failed.
- `pnpm validate:readiness --change associate-ha-sources-with-native-history` — passed after the product owner approved the change.
- `pnpm test:python` — 53 passed on the pinned Home Assistant test environment.
- `uv run ruff check custom_components/tank_os/config_flow.py tests/test_tank_os_home_assistant.py` — passed.
- `uv run ruff format --check custom_components/tank_os/config_flow.py tests/test_tank_os_home_assistant.py` — passed.
- `git diff --check` — passed.

## Limits and notices

- This verifies the pinned Home Assistant release on macOS only. It does not establish a supported Home Assistant version range or compatibility on every installation mode. Native Windows Home Assistant runtime tests remain skipped by the repository test runner; Windows tooling coverage is not HA runtime evidence.
- Tests exercise the integration's options flow and canonical storage boundary. They do not validate behavior against the owner's live Home Assistant instance or guarantee that Recorder retains every entity's history.
- Home Assistant Recorder may exclude or purge history according to its configuration. TankOS does not create canonical telemetry observations in this change.
- `pnpm audit --audit-level=high` reported two advisories below its failure threshold (one low and one moderate). Python product dependency audit skipped because no product requirements file exists.
- OpenSpec reports a warning for the repository-specific `status`, `owner_approval`, and `product_baseline` readiness fields in `.openspec.yaml`; the repository readiness gate reads those fields, and `openspec validate --all` still passed.
