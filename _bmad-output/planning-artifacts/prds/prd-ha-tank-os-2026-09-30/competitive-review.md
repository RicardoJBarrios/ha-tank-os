# External Product Review for ha-tank-os

**Date:** 2026-09-30

**Status:** Research input for product-owner review; not approved scope.

**Purpose:** Review publicly described capabilities of ReefTanker, NextUpReef, and Tankbook before closing the ha-tank-os PRD. This document records observations and recommendations separately from confirmed product decisions.

## Evidence limits

The observations below come from the products' public landing pages on the review date. They describe advertised capabilities, not independent verification of implementation quality, data semantics, pricing durability, mobile-store availability, or Home Assistant compatibility. A feature appearing here must not be treated as an adopted requirement without product-owner approval and, where relevant, a capability or technical review.

## Observed capabilities

### ReefTanker

Publicly presents a free web application focused on reef-parameter tracking. Advertised capabilities include:

- eight core parameters with customizable target ranges;
- ICP report parsing for more than 60 elements;
- Neptune Apex synchronization for pH, temperature, and salinity;
- interactive trends and alerts when parameters drift from targets;
- correlation of maintenance actions with parameter results;
- an alkalinity/calcium/magnesium dosing calculator;
- a salt calculator covering multiple brands and custom recipes;
- action logging for dosing, water changes, and equipment changes;
- mobile-first data entry.

Source: [ReefTanker](https://reeftanker.com/).

### NextUpReef

Publicly presents free iOS and Android reef tracking with a broader automation, advisory, and community scope. Advertised capabilities include:

- parameter logging, trend charts, target bands, and water-change reminders;
- Reef Score and Stability Score;
- AI advice, AI chat, photo-based parameter logging, and stocking advice;
- integrations or control paths involving Apex, HYDROS, ReefRun, Shelly, and other supported pumps/controllers;
- equipment, livestock, cost, dosing, and photo-journal tracking;
- a tablet dashboard and a local tablet hub for selected equipment;
- community leaderboard and tank comparison;
- dosing calculators and schedules that can write schedules to selected devices.

Source: [NextUpReef](https://nextupreef.com/).

### Tankbook

Publicly presents an aquarium log for freshwater and reef keepers, with presets also described for planted, brackish, and pond tanks. Advertised capabilities include:

- logging a full test day quickly;
- editable ideal ranges for tank presets;
- 90-day trend charts with ideal ranges shaded and water changes marked;
- free-text livestock and plant tracking;
- offline maintenance reminders with no account;
- CSV import/export;
- volume, water-change, and unit-conversion calculators;
- a free manual log with unlimited entries and history.

Source: [Tankbook](https://tankbook.app/).

## Comparison with the current PRD

### Already covered by ha-tank-os

- Grouping several measurements into a partial measurement session: [FR-2](./prd.md#fr-2-capture-manual-observations).
- Configurable parameters, starter templates, lifecycle profiles, and target context: [FR-10](./prd.md#fr-10-configure-aquarium-parameters-and-use-templates).
- History, trends, source attribution, event correlation, and separate chemistry series: [FR-4](./prd.md#fr-4-review-latest-values-and-history), [FR-17](./prd.md#fr-17-review-distinct-chemistry-trends), and [FR-19](./prd.md#fr-19-record-aquarium-operations).
- Home Assistant data association and equipment-state provenance: [FR-3](./prd.md#fr-3-receive-automated-measurements-and-equipment-states).
- ICP result handling and analyte preservation: [FR-16](./prd.md#fr-16-associate-manufacturer-lot-analyses).
- Water-change traceability and volume arithmetic: [FR-13](./prd.md#fr-13-trace-prepared-batch-use-in-water-changes) and [FR-14](./prd.md#fr-14-track-storage-container-refills-levels-and-discards).
- Reminders and operation records without implicit actuation: [FR-19](./prd.md#fr-19-record-aquarium-operations).
- Export/import and unit presentation: [FR-8](./prd.md#fr-8-preserve-and-exchange-records) and [FR-9](./prd.md#fr-9-support-languages-locations-and-measurement-systems).

### Candidate improvements to consider

1. **Test-day capture mode.** A focused “full test day” flow could make [FR-2](./prd.md#fr-2-capture-manual-observations) faster without requiring a fixed panel. This fits the existing partial-session decision and should remain configurable by lifecycle phase.
2. **Target-band trend presentation.** Shaded target bands, event markers for water changes, and visible phase context could improve the basic trend views in [FR-17](./prd.md#fr-17-review-distinct-chemistry-trends), provided the target is explicitly attributed to a Tank phase/profile and never presented as a universal standard.
3. **Small transparent calculators.** Water-change volume, unit conversion, and container-volume calculations are aligned with the current traceability model. A calculator should show inputs, units, assumptions, and whether the result is direct or derived.
4. **Offline/manual resilience.** Tankbook's no-account and offline-reminder positioning suggests validating how much of manual capture and review should remain usable when a network service is unavailable. For a local Home Assistant product, this is an architecture/UX question rather than a reason to add a hosted account system.
5. **Optional report ingestion.** ReefTanker's ICP parsing shows potential value in reducing transcription effort. It should be considered only as an optional importer or plugin after the core manual workflow is stable; the PRD's requirement to preserve every analyte and qualifier remains authoritative.
6. **Equipment and livestock extensions.** Equipment context is already present in the PRD. Livestock/plant tracking is not part of the approved initial release and should remain deferred unless the owner identifies a concrete Veril workflow it enables.

### Ideas not recommended for the current product baseline

- Opaque Reef Scores or Stability Scores. They would be derived metrics with unclear method, provenance, target semantics, and risk of hiding the underlying observations. If considered later, they require an explicit method and validation decision.
- AI advice, AI chat, photo interpretation, or stocking recommendations. These are future analysis capabilities, not necessary for the initial trustworthy-record foundation.
- Community leaderboards, social comparison, and public tank profiles. They conflict with the current personal-first, local scope and add privacy and moderation obligations.
- Automatic schedules or commands written to dosing, heating, lighting, or other devices. This conflicts with the current no-actuation boundary in [FR-7](./prd.md#fr-7-prevent-recording-from-causing-physical-actions).
- A parallel Apex/HYDROS/Shelly control layer. The ecosystem-first principle favors consuming suitable Home Assistant entities and services where they satisfy the need, not duplicating device control inside ha-tank-os.

## Product-owner decisions requested

Owner decisions:

- **A.** Approved for the initial release: dedicated configurable “test day” capture mode.
- **B.** Approved for the initial release: target-band and water-change markers in basic trend views.
- **C.** Approved for the initial release: transparent water-change, unit, and volume calculators.
- **D.** Approved as a future near-term optional ICP importer/plugin; manual entry remains the initial core path.
- **E.** Approved as excluded from the initial release, with livestock/plant tracking, scores, AI, and community features eligible for a future near-term review. Device-control schedules remain subject to a separate safety decision.

The owner confirmed these decisions on 2026-09-30. They are now reflected in the PRD and capability map; future near-term candidates remain explicitly outside V1.
