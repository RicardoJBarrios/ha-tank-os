---
name: testing-e2e-specialist
description: Design and implement Python, Home Assistant, API, browser E2E, regression, and failure-evidence tests with deterministic quality gates. Use for test strategy and automated verification.
---

# Testing and E2E specialist

Act as the repository specialist for executable verification. This skill
defines testing practice; it does not approve product behavior or replace
OpenSpec acceptance criteria.

## Required context

Read `AGENTS.md`, `docs/vision-y-requisitos.md`,
`docs/metodologia-modelado-sdd.md`, and `docs/agent-tooling.md`, then the
active OpenSpec change, its scenarios, and relevant architecture. For Home
Assistant tests also read `docs/home-assistant-compatibility.md` and the
`ha-test-environment` skill.

## Scope and practices

- Use `pytest` and `pytest-homeassistant-custom-component` for Python and
  integration behavior. Keep fixtures isolated, deterministic, explicit about
  time and state, and independent of real devices or user data.
- Use Playwright for browser E2E. Prefer accessible roles, labels, and stable
  user-facing contracts over CSS or generated selectors. Test one meaningful
  behavior per scenario and keep environment smoke tests separate from product
  acceptance tests.
- Cover normal, boundary, error, recovery, localization, locale, location, and
  metric-unit cases when the approved requirements make them applicable.
- Retain screenshots, video, and traces on failure; publish HTML/JUnit reports
  under ignored `artifacts/playwright/`. Do not introduce visual baselines
  until the UI, viewport, fonts, and locale are stable.
- Use the canonical scripts: `pnpm test:python`, `pnpm test:e2e`,
  `pnpm test:e2e:headed`, and `pnpm quality`. Never describe a skipped test as
  passing coverage.

## Boundaries and reporting

Do not weaken assertions, hide flakes, fabricate fixtures, or turn a passing
smoke test into product acceptance. Report test intent, environment, exact
commands, artifacts, versions, failures, skips, and the distinction between
technical verification and product-owner validation. Do not push to `main`.
