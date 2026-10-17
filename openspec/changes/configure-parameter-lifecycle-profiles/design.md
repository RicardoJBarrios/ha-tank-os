# Design

## Context

See `proposal.md` and the two spec deltas for scope and behavior. The current canonical store contains Tanks and Observations, but no parameter definitions, aquarium type, lifecycle phase, or profile. Observation parameters are free-text strings; existing observations retain their own reported value and unit. The PRD requires later edits to leave historical meaning intact. The vision lists marine parameter examples, while the approved baseline does not specify the freshwater starter contents.

## Goals / Non-Goals

**Goals:**

- Add locally persisted, Tank-scoped configuration for parameter definitions and lifecycle profiles.
- Make future observations self-describing after configuration is edited or removed.
- Expose configuration through the existing Home Assistant native service and application boundaries.

**Non-Goals:**

- Add a custom frontend or the configurable test-day entry flow planned under CAP-19.
- Define universal target bands, parameter recommendations, testing frequency, conversions, or CAP-20 trend presentation.
- Infer a Tank's current phase from age, recorded observations, or aquarium type.

## Decisions

- **Keep parameter identity separate from labels and units.** Give each Tank parameter a stable ID and a measured-quantity key, with editable label and configured unit metadata. A label change does not change identity; quantities such as nitrate and nitrate-nitrogen use distinct keys. Reject unit input that is not declared compatible with the configured quantity rather than silently converting it. Unit conversion remains presentation work under CAP-17.
- **Copy starter templates into Tank configuration.** Treat freshwater and marine starters as editable initial data, copied into a Tank when selected. Subsequent edits are local to that Tank; a later explicit apply operation is required to change another Tank. This avoids a mutable shared template changing multiple Tanks unexpectedly. Templates include no target ranges or testing schedules.
- **Represent lifecycle phases and parameter profiles as Tank-owned configuration.** Seed cycling, maturation, and established operation. Profiles identify parameters relevant to future capture. Current phase selection is explicit; no phase is inferred and an unset phase produces no selected profile guidance. Editing a phase/profile changes future guidance only.
- **Snapshot interpretation context onto each new Observation.** At capture, store a compact parameter snapshot (stable parameter ID, measured-quantity key, label, configured unit) and phase snapshot (stable phase ID and display name) when those configurations apply. Do not rely only on a live foreign-key lookup: owners may edit or remove configuration later. Existing Observations remain loadable with absent snapshots and are never backfilled with guessed context.
- **Extend the existing local Store with a backward-compatible minor migration.** Add configuration collections with empty defaults for existing installations and optional snapshot fields on Observations. Keep commands and queries behind `ApplicationService` and expose them through native response-capable services; do not write directly from a frontend or adapter.
- **Seed data needs owner confirmation.** Use the existing marine examples as candidates, not universal recommendations. The exact freshwater and marine starter entries are not completely specified by current product authorities; confirm the initial seed manifest before implementation. This does not block the data model or service design.

## Risks / Trade-offs

- [Snapshots duplicate some configuration text in canonical records] → Keep the snapshot limited to fields needed to interpret an Observation and retain source-reported values/units independently.
- [An edited quantity key could make old and new values incomparable] → Make the measured-quantity identity stable after use; create a distinct configured parameter for a different quantity instead of rewriting prior snapshots.
- [Old records lack parameter and phase context] → Keep those fields explicitly absent and do not infer them during migration.
- [A Tank may have no current phase] → Require explicit owner selection and return no selected-profile guidance until one is set.
- [Starter contents could be mistaken for universal advice] → Keep target ranges and cadence out of the starters and identify the final seed manifest as owner-approved data.

## Migration Plan

Add empty parameter/profile collections when loading pre-change storage and allow old observations without snapshots. Do not assign historical phases or parameter definitions. New observations capture snapshots only when matching configuration exists. If a data migration version is required by Home Assistant Store, increment the minor version and test both old and new payloads. Rollback can remove the new service surface; it must not delete configuration or snapshot fields from persisted records.

## Open Questions

- Which exact parameter entries should ship in the freshwater and marine starter manifests? The marine examples are in `docs/vision-y-requisitos.md`; the freshwater list is not specified in the approved baseline. Resolve this owner decision before seeding or enabling the templates.
