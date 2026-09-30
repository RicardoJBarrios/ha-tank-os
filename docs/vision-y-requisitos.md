# Vision and Requirements for ha-tank-os

**Status:** initial project definition. This document records the owner's decisions and keeps open technical questions separate. It does not describe an existing implementation.

**Project directory/name:** `ha-tank-os`.

**Initial target:** Home Assistant, with Veril as the first intended use case.

The process for turning these requirements into a PRD, architecture, specifications, tasks, and milestones is described in [Specification-Driven Product and Development Modeling Methodology](./metodologia-modelado-sdd.md). Installing the tools does not mean that product development has started.

## Purpose

Create a Home Assistant module for managing an aquarium from the same environment that already displays sensors, automations, and notifications. It must accept manually entered data and data received from automated sources, preserve provenance, and allow both to be viewed together.

Some work originally considered for TankOS may be more useful when integrated into Home Assistant. This does not abandon TankOS and does not decide how the two projects will relate in code or data ownership.

## Confirmed decisions

### Platform and scope

- The project has its own directory, `github/ha-tank-os`, separate from `github/veril`.
- The conceptual target is a Home Assistant module, not an indefinite collection of Veril-specific helpers and YAML.
- Veril is the first context. It remains open whether V1 supports only Veril or multiple aquariums from the beginning.
- Values must be accepted from both manual and automated sources.
- Manual and automated data must be queryable and representable in a common model without hiding provenance.
- Reuse suitable Home Assistant capabilities as much as possible and avoid duplicating functionality that HA already provides.
- Prediction is a later phase. The first stage builds a reliable data and history foundation.

### Multilingual product, locations, and measurement systems

- The product must support multiple user-facing languages. Language selection
  must not be hard-coded to English or to the language used by the repository's
  code and documentation.
- User-facing text, labels, help, notifications, validation messages, and
  relevant imported/exported presentation must be localizable. The product must
  define a fallback language for missing translations without changing the
  stored meaning of domain data.
- The product must support multiple user, tank, and operational locations. A
  location may carry locale-relevant context such as country/region and time
  zone, while remaining distinct from the domain `Location` used for tanks,
  samples, equipment, and materials.
- Date, time, number, and decimal formatting must respect the selected locale
  and time zone without changing the canonical meaning or timestamp of a
  record.
- The product must support more than one measurement/unit system, including
  metric/SI presentation and other systems required by users. Users must be
  able to view compatible values in their selected system without losing the
  source value, source unit, precision, qualifiers, or provenance.
- Unit conversion must be explicit and traceable. Stored domain values must not
  be silently rewritten merely because a user changes language, location, or
  display unit preferences.
- Language, locale, physical location, time zone, and unit-system preferences
  are separate concepts and must not be inferred from one another.

### Distribution, license, and contributions

- The project is open source and the public repository uses the MIT license.
- Documentation must explain environment setup, validation and test execution, proposing changes, and contributing.
- Contributor instructions cover macOS, Linux, and Windows. Initial macOS development must not become an implicit requirement.
- Before public release, define policies and channels for contributions, review, issues, security, and releases. Versioned repository documentation remains canonical even if complementary views or services are enabled.

### Development environment and agents

- The initial development machine is a Mac mini with an Apple M4. It is not a product execution requirement or a contribution limitation.
- Visual Studio Code is the primary IDE. Contributors may use other editors; setup instructions cover macOS, Linux, and Windows.
- The initial flow is optimized for Codex while keeping requirements, specifications, instructions, and tasks understandable to other agents.
- Common project instructions remain provider-neutral whenever possible. Provider-specific behavior belongs in separate adapters, skills, commands, or bridges and must not duplicate requirements authority.
- GPT-6 Luna is preferred for tasks it can handle adequately; GPT-6 Astra is reserved for tasks requiring its capabilities. Routing is revisable and must not couple the project to one model.
- Every change must provide enough context for a new agent to work without prior conversation. Routine work should be possible with Luna while gates, review, and human approval remain model-independent.

### Collaboration platform

- GitHub is the repository and collaboration platform.
- Evaluate applicable GitHub Issues, capability planning, Projects, milestones, teams, Wiki, Actions, artifacts, packages, and releases.
- The concrete features, permissions, automation, and possible Wiki use are decided during the PRD and architecture phases. A Wiki must not become a second canonical source.
- Availability depends on repository type, organization, and plan; verify each feature before making it part of the workflow.

### Home Assistant reuse

Start from Home Assistant capabilities. Before implementing a custom feature, check whether entities, services, helpers, automations, Recorder, statistics, history, events, and native UI provide the required semantics and retention.

Add only the aquarium-specific logic that is missing. Do not duplicate entities, records, charts, or services merely for technical preference. If a native feature loses required detail—for example, an aggregate statistic cannot recover every manual analysis—document the limitation and add only the missing capability.

This prioritizes reuse but does not make Recorder the canonical archive of every manual analysis. Persistence must be evaluated against provenance, durability, export, backup, and recovery requirements.

### Digital-twin concept

The module will progressively represent Veril digitally. The goal is not only current values, but relationships between components, measurements, equipment states, operational changes, and time.

The first stage represents observed aquarium state and is not a validated predictive model. Prediction, including anticipating thermal rises to keep water within the target range, comes later after enough data has been collected and compared.

### Mixed sources

Source type must not force incompatible data models. At minimum, each record identifies whether it came from a manual or automated source. Manual capture and automated adapters may differ, but their data remains queryable coherently.

## Planned capabilities

These capabilities define the approved functional direction. They are not implemented and do not close every interaction detail.

### Domain entities and relationships

The model must distinguish, as applicable:

- **Tank:** a managed aquatic unit, initially Veril; it may later include quarantine, auxiliary reservoirs, or other managed systems.
- **Location:** a stable physical or logical place for a sample, sensor, equipment, or material, such as the display, C1/C2/C3, ATO reservoir, or a container. RODI water and prepared salt water describe materials or origins, not locations.
- **Sample:** a concrete collection of water or another material. Several observations may refer to one sample to preserve shared material and sampling time. A sample may originate from Veril, a compartment, RODI water, or a prepared-water batch.
- **Observation:** an original attributed reading, manual or automated. A sample link is optional: a drop test may refer to one, while telemetry may link directly to a sensor/source and location.
- **AquariumEvent and Operation:** a persistent domain event records something that happened, such as cleaning. An operation can relate a target, inputs, outputs, quantities, and execution events. This domain event must not be confused with a transient Home Assistant Event Bus signal.
- **Method, Instrument, and Calibration:** how an observation was obtained and the instrument's metrology state at that time.
- **Product and Lot:** used products, declared formulations, and lot-specific information.
- **Material and MaterialBatch:** substances or prepared batches, such as a batch of salt water, linked to a physical location and to the operation that produces or consumes them.
- **DerivedMetric and Prediction:** calculated or forecast results kept separate from original observations.

Every domain object has its own stable identity, independent of Home Assistant names or `entity_id` values, which may change. Do not create one HA entity for every historical record.

Candidate identifiers include `tank_id`, `location_id`, `sample_id`, `observation_id`, `aquarium_event_id`, `operation_id`, `product_id`, `lot_id`, `material_id`, `batch_id`, `instrument_id`, and `method_id`. Implement only the types included in each phase.

### Time and provenance

Keep distinct timestamps whenever available:

- **Sample collection:** when the sample was obtained.
- **Measurement:** when the test was performed or value observed.
- **Report issuance:** when a laboratory or provider produced the result.
- **Recording:** when the module received or stored the data.

Never invent missing times. Source must be more specific than manual/automated when known: manual entry, HA entity, MQTT, imported report, calculation, manufacturer/provider, or external API, with available source, instrument, method, and import identifiers.

Provenance says where data came from; method says how it was obtained; instrument identifies the measuring device. Do not conflate those roles.

### Information inventory

The module must eventually support these classes, without requiring all sources, importers, or screens in V1:

- **Automated telemetry:** periodic or continuous readings from Home Assistant sensors and integrations, retaining the source entity. Availability in HA does not mean every update must be copied into canonical persistence.
- **Manual and drop tests:** Salifert, Hanna, and other method results, including routine daily controls.
- **Laboratory reports:** ICP-OES and N-DOC results, including every analyte and value present in the received report, not only a fixed set of headline parameters.
- **Aquarium procedures:** water changes, top-offs, dosing, special feeding, cleaning, maintenance, media changes, calibration, livestock additions, and incidents, whether planned or completed.
- **Products, substances, and lots:** anything added to the aquarium or prepared water, with manufacturer/product, lot where available, declared composition or contributions, and available analyses/specifications.

Samples, products, lots, and aquarium water retain distinct contexts. A manufacturer composition is a product declaration, not an independent measurement. A lot analysis describes the source's stated sample or product; it is not a measurement of Veril water and does not prove the final composition of prepared or aquarium water.

### Measurement records

- Record individual measurements or partial sessions; do not require every parameter in every session.
- Support marine parameters such as salinity, pH, alkalinity/KH, calcium, magnesium, nitrate, phosphate, ammonium/ammonia, nitrite, and useful manual temperature checks.
- Preserve every result as a separate observation. A new value must never silently overwrite the previous observation.
- Link observations from the same water draw to one sample. The source may be Veril, a compartment, RODI water, prepared salt water, or another explicit origin.
- Allow observations without `sample_id`, such as periodic automated readings, while retaining the telemetry source/sensor and applicable location.
- Apply corrections append-only: create a linked replacement with a reason and keep the original marked as superseded.
- Distinguish correction, invalidation, and deletion. Correction preserves and points to a replacement; invalidation preserves the record but excludes it as a valid result; deletion means it is no longer presented as active. The exact states and physical-retention policy remain pending.
- Evaluate quality and lifecycle separately. `VALID`, `SUSPECT`, `INVALID`, `SUPERSEDED`, and `DELETED` are candidate vocabulary, not yet approved enumerations or necessarily one state field.
- Preserve applicable sample, measurement, report, and recording times without requiring every source to provide all of them.
- Query the latest known value and measurement time as well as available history.
- Keep the associated method or instrument when known. Method differences matter when interpreting jumps between series.
- Do not assume one measurement frequency for all values.
- Validate parameter and unit and avoid mixing quantities such as `NO3` and `NO3-N`.
- Preserve the source-reported value and original precision. Any conversion or normalization must be traceable and must not hide the original.
- Keep reported value, method/instrument resolution, stated uncertainty, detection/quantification limits, and replicate count separate. Never invent uncertainty.
- Store individual replicates and any reported or calculated result with their relationship explicit.
- Represent a point or an interval/range with limits and unit. Preserve qualifiers such as less than, greater than, not detected, and qualitative; do not silently turn them into exact values.
- Accept variable laboratory panels; a fixed analyte catalog must not prevent storing a new ICP-OES or N-DOC field.
- Associate a report with its laboratory/emitter, sample type and origin, collection date, issue date, units, and declared references when available.
- Attach or link the original report to preserve traceability for transcribed/imported values.
- Separate quality/validity from freshness. A valid but old measurement is not invalid, and an invalid recent measurement is not valid.
- Distinguish the latest chronological observation from the preferred/current value. Preference policy may vary by parameter and must not assume that manual, automated, or any method is always superior.

### Methods, instruments, and calibration

Methods and instruments are referenceable objects. When known, an instrument may include manufacturer, model, and optional serial number. Calibration records retain date, standard, standard lot, nominal value, result, and applied adjustment. An observation may refer to its instrument and the calibration context valid at that time.

### System context and temporal configuration

The model must reconstruct which Veril configuration was active on a date: installed components, sensor/equipment locations, lighting programs, and equipment configuration. Configuration changes retain validity intervals such as `valid_from` and `valid_to` instead of replacing only the current value.

Manual observation capture may take a context snapshot of configured HA entities, such as water and room temperature, known salinity, return/skimmer state, lighting, and thermal state. The snapshot retains sources, timestamps, and freshness and links to the observation. It must not create false manual observations or present stale context as simultaneous. Whether context is copied into canonical persistence or referenced through entity/history records remains pending.

Temporal livestock data may later include species, introduction date, origin, removal date, and reason, so history can be interpreted against the community present at each period.

### Measurement protocols

The module should evolve toward routines that identify required measurements, usual method/instrument, expected frequency, last measurement, and an indicative next date. A “measure KH” routine can show the last result and offer the next capture. Different-frequency measurements may coexist without requiring every one in each session.

### Aquarium events

Planned event records include water changes and changed volume, top-off, equipment cleaning, resin changes, livestock additions, manual dosing, ICP/N-DOC analysis, maintenance, incidents, and other relevant operational changes.

Events retain their own identity and time. They are not measurements and must not be stored as parameter values, although they may appear in a timeline or beside charts.

Complex operations relate inputs, outputs, and purpose. Preparing water may consume RODI water and salt from a lot and produce a salt-water batch; a water change may consume that batch and target Veril; dosing may consume a product quantity and target the aquarium. Quantities and relationships remain declared or measured; unobserved chemical balances are not inferred.

### Water preparation and additions

Each addition is its own operation linked to the product, declared composition, and lot or lot analysis when available. Record what was added, how much, when, and where: directly to the aquarium, to a water change, or to another preparation. Preserve the unit and dosing basis, such as product mass or volume per water volume, when known.

Manufacturer, provider, or report claims about a product's contributions are stored with source, unit, concentration/proportion, and reference basis. They are labeled as declared composition/specification or lot analysis, not as a measurement of what dissolved or reached the aquarium.

## Home Assistant integration

The integration must use Home Assistant's configuration flow. Do not declare `single_config_entry: true` before the multi-aquarium scope is settled; that option limits the integration to one configuration entry and does not define a multi-tank domain model.

The domain model is independent of the HA device registry. A `Tank`, `Location`, or compartment must not be assumed to equal an HA Device or child device. The number of Config Entries must not implicitly define the number of Tanks.

The integration must provide a clear boundary between domain persistence and HA projections. It should expose only current, useful projections as entities and must not create an entity for each historical record. It must not allow recording a measurement or event to actuate equipment by itself.

Localization and unit preferences must be represented without making Home
Assistant's entity names or display strings the canonical source of domain
meaning. The integration may reuse HA locale and unit settings where their
semantics are sufficient, but it must preserve domain provenance, source units,
and canonical timestamps.

## Proposed technical direction

### Layer separation

Keep domain rules and models independent of Home Assistant so they can be tested without starting HA. Keep adapters, persistence, HA integration, and presentation at explicit boundaries.

### Backend and integration

Python is the current preferred language for a Home Assistant integration. `dataclasses` and Pydantic v2 are candidates for model validation; the choice depends on compatibility, complexity, and acceptable dependencies.

Potential HA adapters include entities, services/actions, events, Config Flow, Config Entries/Subentries, and WebSocket commands. Their exact contracts remain to be designed and verified against supported HA versions.

### Persistence and history

SQLite or another local store is a candidate canonical backend, but no backend has been selected. The decision must cover migrations, backup, recovery, concurrency, export/import, and retention. Home Assistant Recorder and statistics may complement domain records but must not replace detail required to interpret an individual analysis.

### Backend, Home Assistant, and frontend contracts

The module must distinguish domain records, HA entities, events, actions, and frontend queries. A frontend must not treat an aggregate, prediction, or historical summary as a current measurement. A custom WebSocket API is only justified if native HA mechanisms cannot provide the required information.

### Interface by use case

Evaluate native HA UI and Config Flow first. A custom card, panel, or frontend package is considered only when a concrete user flow cannot be served adequately by native capabilities. TypeScript + Lit is a current option for evaluation, not a final decision.

### Provisional stack

| Area | Candidate | Status |
| --- | --- | --- |
| Home Assistant integration | Python | Preferred direction; verify against supported Core versions |
| Domain validation | `dataclasses` or Pydantic v2 | Pending compatibility test |
| Canonical persistence | SQLite or managed local storage | Pending ADR |
| Frontend extension | Native HA UI first; TypeScript + Lit only if needed | Pending flow evaluation |
| Development and agents | VS Code, Codex, BMAD, Spec Kit, OpenSpec | Installed; interoperability pilot pending |

## Scheduling, alarms, and actions

The module may later support measurement routines, recurring plans, reminders, notifications, and acknowledged alarms. These features must remain distinct from observations and events, and their phase and contracts are pending.

No recorded measurement or event may trigger dosing, heating, cooling, or another external action by itself. Any future action requires explicit authorization, permissions, safeguards, validation, and a separate design.

## Persistence and quality requirements

Preserve source values, units, precision, qualifiers, provenance, methods, instruments, applicable timestamps, corrections, invalidations, and relationships. Preserve original data append-only when correcting it. Keep quality, lifecycle, and freshness distinct. Design deduplication and import conflict rules without silently losing information.

Export/import must preserve identifiers, relationships, source semantics, qualifiers, and round-trip meaning. Backup and recovery must be evaluated against the chosen persistence backend.

## Derived metrics and predictions

A derived metric identifies its algorithm and version, inputs, and calculation time. Future examples include daily KH consumption, a 24-hour thermal mean, or change since an operation.

A prediction identifies target variable, generation time, horizon, predicted value, interval or uncertainty expression when provided by the method, and model/version. It can later be linked to the corresponding real observation to evaluate error. Never invent statistical confidence.

## Initial implementation priority

The proposed V1 cut reduces the initial core to `Tank`, `Location`, `Method`, `Instrument`, `Sample`, and `Observation`, plus observation/session creation, correction, latest/preferred lookup, history, and export/import. It proposes deferring `AquariumEvent` to V1.1 because it does not demonstrate a different architectural capability from observation capture. This is a proposed baseline to confirm in the ADRs before the first vertical slice.

The proposed first vertical slice records a manual KH result, for example from Salifert; persists it; projects the preferred value as `sensor.veril_kh`; opens its session; corrects it without deleting the original; exports and imports it while preserving relationships; and verifies that after restarting Home Assistant the entity projects the last valid/preferred value read from canonical persistence. It also checks behavior when that persistence is unavailable. The example defines an architectural test, not a real Veril measurement.

The architecture must leave room for automated ingestion and a common manual/automated observation model, but V1 does not require general automated connectors. HA context snapshots are optional for the initial cut until their copy-versus-reference policy is decided.

If the proposed cut is retained, `AquariumEvent`, broader operations, and action-recording features move to later phases without being removed from the evolutionary scope. V1 does not implement product inventory/consumption, full lot management, temporal livestock, scheduling, alarms, automatic ICP import, advanced analytics, or prediction. These must remain possible in the model. Planning and alarms remain product requirements but are outside the proposed initial cut.

Before functional code, five architectural decisions should be closed and recorded as ADRs:

1. **Config Entry, Config Subentry, and Tank:** relationship between Home Assistant configuration and the multi-tank domain model.
2. **Canonical persistence:** SQLite or another option, migrations, backup, recovery, and export/import.
3. **Minimum V1 model:** schema, stable identities, correction, invalidation, and deletion.
4. **Home Assistant contract:** automated ingestion/retention, projection restoration at startup, exposed entities/actions/events, and what remains only in domain persistence.
5. **Interface contract:** what native Config Flow/UI solves and what requires a card, panel, or custom WebSocket, including the frontend technology.

After these ADRs, the next proposed objective is to design and validate the vertical slice above. This is a recommended design gate, not evidence that the ADRs or implementation already exist.

## Digital-twin evolution

The intended evolution is staged:

1. **Recording and visualization:** capture measurements/events, show latest values, and query history.
2. **Connected representation:** bring relevant manual data and automated telemetry together in Home Assistant.
3. **Temporal relationships:** compare measurements with water changes, maintenance, lighting, equipment state, and dated operations.
4. **Descriptive calculations:** add trends or rates labeled as calculations, not observed readings.
5. **Prediction:** estimate future responses only after sufficient data and validation against real observations.
6. **Prediction-based automation:** consider automatic actions only after evaluating prediction error, uncertainty, and safeguards.

### Future thermal-prediction example

A future goal is to anticipate a rise in water temperature and act early enough to keep it within Veril's adopted thermal range. Relevant chronological inputs could include water temperature, room and Santa Cruz de Tenerife weather temperature, the Rowenta's observed physical state and known digital state/mode/setpoint/fan, lighting, other operational changes, and the time, duration, and aftermath of each episode.

Analysis must distinguish observations, digital commands, confirmed physical states, and inferences. A correlation or one before/after episode is not causal validation by itself.

## Persistence and history

Home Assistant history and statistics are useful for dashboards and time series, but Recorder is not yet chosen as the permanent canonical archive of every manual analysis.

`ha-tank-os` domain records are authoritative for samples, observations, operations, products, and lots. Home Assistant entities are projections of relevant current state, not the canonical record and not one entity per historical row. The persistence technology remains pending.

Persistence must retain enough original information to reconstruct what was measured, when, and through which source or method. Aggregated statistics may complement records but cannot replace individual detail. The backend must support backup, recovery, and export.

If consistency requires coordination—such as pausing writes or preparing a local database—evaluate Home Assistant Backup hooks (`async_pre_backup` and `async_post_backup`). Do not implement them if the persistence mechanism already provides suitable consistency.

## Current limits

- No product code, integration, interface, or data schema is implemented.
- No Home Assistant entities have been created for this module.
- No persistence backend, input protocol, or export/import format has been selected.
- Append-only correction, quality/freshness separation, and deduplication are requirements whose mechanisms and detailed criteria remain pending.
- The ICP-OES/N-DOC import format, complete analyte structure, and attachment handling remain undefined.
- Products, declared contributions, lots, and linkable operations are required in the domain, but detailed schema and inventory management remain pending.
- The per-parameter policy for preferred versus latest chronological observation is not defined.
- Context-snapshot entities, age limits, and copy-versus-reference policy remain undefined.
- Invalidation/deletion policy and logical-versus-physical deletion timing remain undefined.
- Permissions for reading, capture, correction, deletion, configuration, and external-effect operations remain undefined.
- A lossless semantic interchange format has not been selected or validated.
- It is not decided whether persistence needs Home Assistant Backup hooks.
- Automated telemetry ingestion and retention criteria remain undefined.
- Startup/reload reconstruction and the projection state when persistence is unavailable remain undefined.
- Deferring `AquariumEvent` to V1.1 remains a proposal pending ADR confirmation.
- The five pre-vertical-slice ADRs are proposed but have not been written or approved.
- No prediction algorithm has been designed or validated.
- Recorded data is not authorized to actuate dosing, heating, cooling, or other equipment by itself.

Creating this directory and document does not create or initialize a remote Git repository.

## Open technical decisions

These questions require later design and must not be resolved by inference:

1. Integration/presentation boundary and any remaining native-HA gaps.
2. Canonical persistence, including SQLite versus managed local storage, migrations, backup, recovery, concurrency, and export.
3. Record model: required/optional fields, units, precision, optional samples for automated observations, duplicates, corrections, invalidation, deletion, and timestamps.
4. Initial automated sources, ingestion, deduplication, thresholds, sampling, and retention; evaluate `DataUpdateCoordinator` only for periodic-query adapters.
5. HA representation: exposed measurements, age and quality, long-term-statistics eligibility, and projection restoration.
6. Event catalog, structure, and capture mode.
7. Scheduling and alarms: conditions, recurrence, states, acknowledgement, notifications, and phase.
8. Temporal validity for locations, sensors, equipment, configuration, and livestock.
9. Installation scope and multi-tank interface, including Config Entries and Config Subentries; entry count must not define tank count.
10. Responsibility boundary and canonical authority if TankOS and ha-tank-os evolve together.
11. Frontend contracts and whether native UI suffices or custom card/panel/WebSocket is needed.
12. Whether Tanks or Locations should be projected as HA Devices or child devices; the domain must remain independent.
13. Distribution, lifecycle, versioning, supported Home Assistant versions, and backup policy.
14. Thermal prediction variables, horizon, validation, uncertainty, and safety conditions before influencing control.
15. Context snapshots: copied values versus HA entity/history references, age, and Recorder purging effects.
16. Authorization for reads, capture, correction, invalidation, deletion, configuration, and external-effect operations.
17. Import/export format, identifier preservation, semantic round-trip, and import conflict rules.
18. Backup integration requirements.
19. Whether `AquariumEvent` belongs in V1 or V1.1 and when to write the five pre-slice ADRs.
20. Supported languages, translation ownership, fallback behavior, locale/time-zone scope, and how language preferences relate to Home Assistant users.
21. Canonical units, supported display-unit systems, conversion precision, qualifiers, source-unit retention, and per-user versus per-tank preferences.

## Context references

- [Home Assistant Recorder](https://www.home-assistant.io/integrations/recorder/)
- [Home Assistant statistics](https://data.home-assistant.io/docs/statistics/)
- [Home Assistant integration architecture](https://developers.home-assistant.io/docs/architecture_components/)
- [Home Assistant Config Flow](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/config-flow/)
- [Config Entries and Subentries](https://developers.home-assistant.io/docs/config_entries_index/)
- [ConfigEntry runtime data](https://developers.home-assistant.io/blog/2024/04/30/store-runtime-data-inside-config-entry/)
- [Integration manifest](https://developers.home-assistant.io/docs/creating_integration_manifest/)
- [Integration file structure](https://developers.home-assistant.io/docs/creating_integration_file_structure/)
- [WebSocket API extensions](https://developers.home-assistant.io/docs/frontend/extending/websocket-api/)
- [Custom panels](https://developers.home-assistant.io/docs/frontend/custom-ui/creating-custom-panels/) and [custom cards](https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/)
- [Asyncio and blocking operations](https://developers.home-assistant.io/docs/asyncio_blocking_operations/)
- [Home Assistant Backup platform](https://developers.home-assistant.io/docs/core/platform/backup/)
- [Calendar entity](https://developers.home-assistant.io/docs/core/entity/calendar/)
- [Actions in integrations](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/action-setup/)
- [Repairs](https://developers.home-assistant.io/docs/core/platform/repairs/) and [System Health](https://developers.home-assistant.io/docs/core/integration/system_health/)
- [Frontend component changes in 2026.4](https://developers.home-assistant.io/blog/2026/03/25/frontend-component-updates-2026.4/)
- [Device registry changes in 2026.8/2026.9](https://developers.home-assistant.io/blog/2026/08/19/device-registry-websocket-api-changes/)
- [Configurator deprecation](https://developers.home-assistant.io/blog/2026/08/31/deprecate-configurator/)
- [Recorder statistics API changes](https://developers.home-assistant.io/blog/2025/10/16/recorder-statistics-api-changes/)
- [Home Assistant sensor entity](https://developers.home-assistant.io/docs/core/entity/sensor/)
- [Aquarium Monitor Card](https://github.com/wilsto/aquarium-monitor-card), consulted as a visualization reference but not adopted as a dependency or substitute for the required measurement/event record.

## Provenance and reading criteria

This document consolidates the design conversation of September 29, 2026 and the owner's supplied texts and AI proposals about the data model, technical architecture, and architectural refinements. Examples of values and objects are illustrative, not current Veril measurements or configuration. Technical recommendations are linked to official documentation when checked; implementation choices that are not closed remain candidates or pending decisions.

When a technical decision was not explicitly closed, it remains pending. Future phases describe design intent, not implementation or a schedule commitment.
