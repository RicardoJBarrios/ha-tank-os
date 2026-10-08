# Tasks

## 1. Home Assistant association configuration

- [x] 1.1 Add an options flow with native entity and Tank/Domain Location selectors; verify the flow lists only current canonical targets and saves stable target IDs in Config Entry options.
- [x] 1.2 Add association update/removal and stale-reference handling; verify renamed or removed entities and deleted targets remain unresolved until explicit user correction or removal.
- [x] 1.3 Add Home Assistant config-flow strings and Spanish translations for association setup, unresolved references, validation errors, and removal; verify translation files parse and all displayed keys resolve.
- [x] 1.4 Add focused Home Assistant tests for Tank and Domain Location association, update/removal, entry reload, invalid targets, unresolved references, and preservation of canonical records; verify with `pnpm test:python`.

## 2. Native history reuse and delivery evidence

- [x] 2.1 Verify associations do not create canonical Observations, subscribe to entity state changes, or change Recorder options; add a regression test and verify it with `pnpm test:python`.
- [x] 2.2 Document how to review an associated entity in Home Assistant's native History UI and explain that Recorder filters and purges govern availability; verify the documented path matches the supported UI and contains no promise of permanent retention.
- [x] 2.3 Run `pnpm quality:checks` and `git diff --check`; record the pinned Home Assistant and Python versions plus the results and limits in the change evidence before delivery.
