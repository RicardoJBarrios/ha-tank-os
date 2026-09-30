# ha-tank-os Global Capability Map

**Status:** Initial product-baseline artifact

**Source of truth:** [Product Requirements Document](./prds/prd-ha-tank-os-2026-09-30/prd.md)

**Supporting source:** [PRD Addendum](./prds/prd-ha-tank-os-2026-09-30/addendum.md)

This map is derived from the owner-approved PRD. It is a product-level map, not an implementation plan, architecture, backlog, or OpenSpec change. Technical feasibility and Home Assistant capability fit remain subject to architecture review.

## Capability groups

| ID | Capability | Initial release boundary | Priority | Depends on |
| --- | --- | --- | --- | --- |
| CAP-01 | Aquarium and context management | Multiple Tanks; Domain Locations; stable domain identities; Veril is the first intended Tank | Must | — |
| CAP-02 | Manual observation capture | Standalone and grouped partial sessions; Samples; methods; instruments; qualifiers; distinct timestamps | Must | CAP-01 |
| CAP-03 | Home Assistant source association and ingestion | Owner association plus reviewable suggestions; selected relevant sensor and equipment data; provenance retained; no actuator control | Must | CAP-01, CAP-02, HA capability review |
| CAP-04 | History and current-value review | Chronological history; latest valid observation shown with source/context; direct records remain traceable; native HA history reused where suitable | Must | CAP-02, CAP-03 |
| CAP-05 | Configurable parameters and lifecycle profiles | Editable freshwater and marine starters; cycling, maturation, established operation; owner-added phases and parameters | Must | CAP-01, CAP-02 |
| CAP-06 | Prepared-water batch traceability | Freshwater/saltwater batches; source volume; salt product/quantity/lot; optional final salinity; no chemical estimates | Must | CAP-02, CAP-05 |
| CAP-07 | Water transfer and storage traceability | Water-change transfers; graduated-container observations; refills; withdrawals; discards; derived amounts kept distinct from direct observations; freshwater/saltwater contents cycles separated | Must | CAP-06 |
| CAP-08 | Manual top-off recording | Manual freshwater/saltwater top-offs linked to Tank and known source; periodic container observations may support derived amounts; no required ATO integration | Must | CAP-07 |
| CAP-09 | Manufacturer lot-report records | Manual source link, attachment, transcription of every reported analyte; exact salt-lot attribution; optional plugin retrieval only | Must | CAP-06 |
| CAP-10 | Prepared-water direct measurements | Measurements linked to exact batch and Sample where applicable; distinct from manufacturer reports and estimates | Must | CAP-06, CAP-02 |
| CAP-11 | Basic chemistry trend views | Separate source-water TDS, lot-report, prepared-water, and aquarium-water series; contextual timestamps and traceable points | Should | CAP-04, CAP-06, CAP-09, CAP-10 |
| CAP-12 | Basic aquarium operations | Planning and completion for dosing, cleaning, and maintenance; product/lot/quantity or affected equipment as applicable; no recurring schedules in V1 | Must | CAP-01, CAP-04 |
| CAP-13 | Operation reminders | One-off reminders and alerts through native or selected HA notification capabilities; notifications never execute operations | Should | CAP-12, HA capability review |
| CAP-14 | Configurable process capture | Built-in optional fields plus owner-defined text, numeric-with-unit, yes/no, and predefined-choice fields; required/optional/unknown semantics | Must | CAP-02, CAP-06, CAP-07, CAP-12 |
| CAP-15 | Direct correction and dependency-safe deletion | Edit/delete active records directly; block deletion with unresolved dependencies; no silent cascades | Must | CAP-02, CAP-06, CAP-12 |
| CAP-16 | Portability and recovery | Owner-controlled export/import or equivalent; preserve identities, relationships, provenance, values, units, qualifiers, and timestamps | Must | CAP-01–CAP-15 |
| CAP-17 | Localization and measurement presentation | Spanish and metric initially; installation defaults plus per-user overrides; extensible languages and unit systems; canonical values unchanged | Must | CAP-01–CAP-16 |
| CAP-18 | Ecosystem capability fit | Review HA Core and suitable plugins before custom work; present small residual gaps to the owner before adding scope; simplify requirements when appropriate | Must | Applies to all capabilities |
| CAP-19 | Configurable test-day capture | Phase-aware parameter entry for a partial or complete test session; no fixed panel required | Must | CAP-02, CAP-05 |
| CAP-20 | Contextual trend annotations | Target bands from Tank/profile context and recorded water-change markers without causal claims | Must | CAP-04, CAP-05, CAP-12 |
| CAP-21 | Transparent aquarium calculators | Water-change, unit-conversion, and graduated-container calculations with explicit inputs and direct-versus-derived semantics | Must | CAP-07, CAP-08, CAP-17 |

## Initial-release exclusions

- Autonomous dosing, heating, cooling, or other physical control.
- Prepared-water chemical contribution estimates and validated prediction.
- General inventory management, livestock management, recurring operation schedules, and broad external connectors.
- Required ATO integration.
- TankOS migration, interoperability, data exchange, or runtime dependency.
- Livestock/plant tracking, scores, AI, community features, and automatic ICP parsing are future near-term candidates, not initial-release capabilities.

## Capability sequencing

1. Establish domain identity, persistence authority, provenance, and manual observation capture (`CAP-01`, `CAP-02`).
2. Validate Home Assistant reuse and source association before selecting custom presentation or ingestion (`CAP-03`, `CAP-18`).
3. Provide trustworthy history, configurable parameters, correction, deletion, and portability (`CAP-04`, `CAP-05`, `CAP-15`, `CAP-16`).
4. Add prepared-water, storage, transfer, top-off, report, and direct-measurement flows (`CAP-06`–`CAP-10`).
5. Add operations, reminders, process configuration, trends, calculators, and localization within the approved safety and provenance boundaries (`CAP-11`–`CAP-14`, `CAP-17`, `CAP-19`–`CAP-21`).

## Deferred capability decisions

- Home Assistant versions and installation modes.
- Canonical persistence failure behavior, migration, backup rotation, and recovery objectives.
- Telemetry selection, sampling cadence, and retention boundary between canonical records and native HA history/Recorder.
- Detailed UX, accessibility targets, performance limits, and plugin dependency policy.
- Evidence and acceptance criteria for any future digital-twin inference or prediction.
