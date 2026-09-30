# End-to-End Testing Strategy

Playwright is the browser automation boundary for Home Assistant UI journeys.
Python tests remain the fast integration boundary for Home Assistant APIs and
custom integration behavior. The two layers must not be treated as substitutes.

## Test levels

| Level | Scope | Default trigger | Evidence |
| --- | --- | --- | --- |
| Unit | Pure product logic | Every change | Test result and coverage |
| Python integration | Home Assistant APIs, config flow, entities, storage | Every integration change | Test result, HA/Python versions |
| Browser smoke | Local HA surface is reachable | Local preflight | HTML/JUnit report |
| Browser E2E | Approved user capability from UI to visible outcome | Capability change and regression suite | HTML/JUnit, screenshot/video/trace on failure |
| Visual regression | Stable product UI pixels at declared viewport and locale | UI change | Reviewed snapshots and diff report |

## Case design

Every product journey should have a stable identifier and state its risk:

```text
E2E-<capability>-<number>: <user-visible outcome>
Risk: critical | high | medium | low
Preconditions: isolated HA state and required credentials
Steps: semantic user actions
Assertions: visible outcome and relevant API/state evidence
Cleanup: deterministic reset or disposable test data
```

Use role, label, and accessible-name locators before CSS selectors. Avoid
asserting Home Assistant internals or implementation-specific DOM structure
unless the test explicitly covers a compatibility boundary.

## Regression policy

- Smoke tests may run without onboarding credentials.
- Authenticated journeys must use an operator-provided local storage state or
  token that is outside Git and outside test reports.
- A regression test must reproduce a known failure or protect an approved
  requirement; do not add tests only to increase the count.
- Tests that depend on time, locale, units, location, or measurement systems
  must declare those settings and cover the supported product matrix
  deliberately.
- Product acceptance remains a product-owner decision even when all automated
  checks pass.

## Reports and media

Playwright writes the HTML report and JUnit XML under
`artifacts/playwright/`. Failed tests retain their screenshot, video, and trace
for diagnosis. These files are local evidence and are ignored by Git. Visual
snapshots must not be introduced until the product UI, browser viewport, fonts,
locale, and data state are deterministic.

Run the current layer with `pnpm test:e2e`, inspect a report with
`pnpm test:e2e:report`, and use `pnpm test:e2e:headed` for interactive
diagnosis.

## Continuous integration

The repository workflow runs the environment browser smoke test on Ubuntu with
the pinned Home Assistant container and Chromium. This verifies that the
disposable HA target can start and that its initial browser surface opens. It
does not replace product journeys or product acceptance tests, which remain
pending the approved product baseline.
