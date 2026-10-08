# E2E Test Areas

This directory contains browser tests for the local Home Assistant target and,
after the product UI is approved, for product user journeys.

## Test boundaries

- `ha-smoke.spec.ts` verifies that the local Home Assistant HTTP/UI surface is
  reachable. It is an environment smoke test, not product acceptance.
- Product journeys must be organized by user capability and must use semantic
  locators, visible outcomes, and isolated test data.
- Authenticated tests must use locally provisioned credentials from environment
  variables or a secret store. Never commit tokens, cookies, or storage state.
- Visual snapshots must be added only after the target UI, viewport, fonts, and
  locale are stable. Review snapshot changes as artifacts; do not approve them
  only because Playwright generated them.

## Evidence

Playwright retains screenshots, videos, and traces for failed tests. Reports are
written to `artifacts/playwright/` and are ignored by Git. The HTML report and
JUnit output are technical evidence; they do not replace product-owner
validation.
