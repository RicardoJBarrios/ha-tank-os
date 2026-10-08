# Architecture Review — Boundary and Seam Check

## Verdict

No critical incompatible-unit construction was found in the current spine. The main ownership seams are explicit: the domain owns canonical records, the repository owns persistence access, adapters translate external inputs, Config Entries own integration configuration, and Home Assistant entities/Recorder own projections or selected telemetry.

## Checked seams

- Manual input versus Home Assistant ingestion: one application write core.
- Canonical repository versus Recorder: separate authorities and retention semantics.
- Domain events versus HA event bus: commit first; downstream effects do not define history.
- Plugins versus core: optional adapters cannot bypass contracts or persistence.
- Planned operation versus notification: stored facts remain distinct from scheduling and delivery.
- Current projections versus historical records: no entity-per-record model.

## Deferred items

- Exact repository transaction and migration contracts.
- Duplicate fingerprint format and conflict UX.
- Projection rebuild and stale-state behavior.
