# Test Automation Summary

## Current coverage

- [x] `tests/e2e/ha-smoke.spec.ts` — local Home Assistant onboarding or
  application surface opens.
- [ ] Product API and integration tests — pending approved integration scope
  and product baseline.
- [ ] Product browser journeys — pending approved capabilities and UI scope.
- [ ] Visual snapshot baselines — intentionally deferred until the product UI,
  locale, viewport, fonts, and test data are stable.

## Commands

- `pnpm test:python` — runs Python integration tests when repository tests exist.
- `pnpm test:e2e` — waits for Home Assistant and runs Chromium E2E tests.
- `pnpm test:e2e:report` — serves the HTML report from the latest run.

The smoke result is technical environment verification. It is not product
acceptance or proof of Home Assistant integration compatibility.
