# PRD Addendum: Prepared Saltwater Batch Tracking Research

**Status:** Research notes and candidate requirements for owner review. These findings inform discovery; they do not amend approved scope without the owner's decision.

**Research date:** 2026-09-30

## Research question

What should ha-tank-os consider when recording prepared saltwater and preserving the evidence that could inform a future decision about composition estimation?

## Product comparisons

Public feature descriptions from aquarium log products show several recurring patterns:

- [ReefTanker action logging](https://reeftanker.com/features/action-logging/) describes recording water-change volume, salt brand and batch, pre/post parameters, and process notes, and linking actions to parameter readings. This is a close analogue for traceability, but its published feature description is not a full data-model specification.
- [NextUpReef feature descriptions](https://nextupreef.com/features) describe tank-specific parameter selection (adding/removing parameters), user-defined target ranges, trend charts, and water-change markers. This supports configurable parameter sets and temporal context around actions.
- [Tankbook](https://tankbook.app/) describes editable presets for freshwater, planted, brackish, saltwater, reef, and pond setups, with editable target ranges. This supports the proposed pattern of editable starter templates rather than one fixed parameter set.

These are product examples, not endorsements or evidence that their implementations are technically suitable for ha-tank-os. Public feature pages do not establish whether they preserve raw records, lot-level lineage, or calculation uncertainty.

## Manufacturer and measurement-method considerations

- Aquaforest's [salt batch ICP page](https://aquaforest.eu/en/check-your-salt/) says its salt is tested by production batches, with three samples collected per batch and dissolved in 15 litres of RO water for ICP-OES. It describes a 600 kg batch and says container-to-container parameters may vary by around 2–3%. Therefore, a lot report is useful source evidence but is not a direct assay of the exact container or the owner's prepared water.
- Aquaforest's instructions on the same page recommend recording/checking the salinity at which a salt sample was prepared; the tested parameters vary with salinity. It specifies a standardized preparation and salinity-measurement context for interpreting the report. The product should preserve the report's preparation basis if available, separately from the owner's preparation.
- The [U.S. Geological Survey](https://www.usgs.gov/index.php/water-science-school/science/water-science-glossary) describes specific conductance as a means of approximating total dissolved solids. Conductivity/TDS alone does not identify which ions or substances are present. It can be retained as a source-water quality observation, but must not be treated as an ion-specific analysis of the source water.
- Aquarium forums include practical advice to check the final salinity/specific gravity, bring water to an appropriate temperature, and account for temperature effects on specific-gravity readings. For example, this [ReefsForum salt-mixing discussion](https://www.reefsforum.com/threads/marine-salt.5782/) is a dated, product-specific discussion, not a universal standard. Product-specific instructions and the user's actual procedure take precedence over forum anecdotes.

## Candidate record fields for owner review

### Confirmed minimum from the owner

- Source-water volume.
- Whether a prepared batch contains freshwater or saltwater, and its own stable identity.
- Source-water volume and a link to the source-water TDS reading when available.
- Independent source-water TDS observations and history for monitoring water-treatment output, using an existing suitable Home Assistant sensor/history or manual entry.
- For saltwater batches: salt product/type, salt quantity and unit, specific lot/batch identifier, and link to the lot's ICP report when available.
- Manual source-linking, report-file attachment, and/or transcription of the manufacturer ICP report, associated with the exact salt lot.
- Transcription of every ICP analyte shown in the lot report, even when the analyte is not configured in a Tank template; preserve the report's names, units, qualifiers, and stated limits/context.
- Amount transferred from the batch on each use, linked to the destination Tank and Water Change Record.
- Storage Container identity, refill events, observed fill levels/volumes, and water type for each refill cycle.
- For marked containers, either the directly added volume (such as 1 L) or a direct current-volume observation (such as X L remaining); keep these entry meanings distinct.
- Recorded discarded batch/container water so it is not counted as delivered to a Tank.
- Top-Off Records for manual or ATO-driven additions, with water type, Tank, source container/batch, and directly available or derived amount clearly distinguished.

### Recommended optional context to consider

- Source water identity and treatment context (for example RO/DI and relevant filter stage), source TDS value/unit, observation time, and meter/instrument when known.
- Final prepared-water volume, kept distinct from initial source-water volume because they are not necessarily interchangeable.
- Measured final salinity (including representation/unit), measurement time, water temperature at measurement, instrument/method, and calibration context when known.
- Preparation time, mixing duration and procedure, temperature, and notes about dissolution, precipitation, or other observed anomalies.
- The manufacturer's ICP report artifact or stable reference, exact lot code, report date, analyte values, units, qualifiers/detection limits, and the manufacturer's sample-preparation basis when available.
- Container capacity or level-to-volume calibration details and how they are maintained.
- ATO source integration, event meaning, and whether the system reports flow/volume or only state transitions.
- Water temperature, preparation/mixing duration, and process notes where useful.

Not all candidates need to be required. The initial release records measurements, manufacturer-reported values, and process notes as distinct evidence; it does not infer prepared-water chemical composition from them.

### Owner decision: missing final salinity

Final salinity is recommended and should be recorded with measurement context when available, but it is not a gate that prevents a batch from being used. If absent, the product must show a clear warning that the batch has not been checked. No prepared-water chemical estimate is calculated in the initial release, regardless of whether final salinity is available.

### Owner decision: configurable process data

Across supported process types, the owner can configure which context fields are collected by selecting built-in fields and defining custom fields, and mark configurable fields required or optional for that process type. Custom fields support text, numbers with optional units, yes/no values, and predefined choices. A required field can be completed with a value or an explicit unknown/not-measured state, distinct from empty and zero; an optional reason may explain why it is unknown. Preparation temperature, mixing duration, and mixing procedure are optional examples, not required fields for every batch unless the owner configures otherwise. Fields essential to identify and trace a process record cannot be disabled.

### Owner decision: direct record editing and deletion

The owner can edit or delete records directly; edits do not require linked replacement records. A deleted record is removed from active product records. To avoid accidental loss and keep referential handling simple, deletion must not silently cascade to dependent records; the owner resolves blocking relationships before deleting the target. Backup-retention behavior remains for architecture and data-lifecycle design.

### Owner-provided reference: Veril phase-dependent measurement plan

The owner's existing Veril plans are an input example for configurable, phase-dependent measurement profiles, not universal aquarium standards or verified operating results. During cycling, the plan emphasizes total ammonia nitrogen/ammonia and nitrite; its runbook calls for daily measurements of those parameters, pH, and temperature, with salinity and alkalinity recorded at the cadence specified by the plan. Nitrate and phosphate are optional supporting baseline measurements. After cycling, the maturation plan tracks NH3/NH4 and NO2 for safety, NO3 and PO4 as nutrients, pH and alkalinity, and salinity and temperature. Calcium, magnesium, and alkalinity become relevant when calcifying organisms, measured consumption, or dosing make them applicable.

The local Veril plan adopts a preferred temperature zone of 25–26 °C, an operational normal range of 24.5–26.5 °C, and practical salinity target `S_P = 35`. These are Veril-specific settings, not default product targets. The plan does not set one universal target table for every phase and parameter; cycle acceptance depends on the test method's limits and confirmation period. Source documents reviewed on 2026-09-30: Veril's cycling runbook, maturation plan, and recurring measurement-and-test plan.

### Owner decision: editable lifecycle phases

The initial lifecycle phase set includes cycling, maturation, and established operation. The owner can add and modify phases and their associated measurement profiles. Changing a phase or profile affects future capture guidance; it does not rewrite the phase context of historical Observations.

### Owner decision: configurable preparation context

No extra preparation measurements or context fields are required by default beyond the previously agreed batch identity, source-water volume, and applicable salt/lot details; final salinity is recordable when measured but does not block use. The owner configures any additional preparation context fields and whether each is required or optional.

### Owner decision: automated Home Assistant data and future integrations

Relevant data already exposed by Home Assistant—including sensor measurements such as temperature and humidity, plus available actuator/equipment readings and state changes—must be received automatically when associated with the managed Tank, location, or equipment. The owner can configure an association manually or review/accept an automatic association suggestion; unaccepted suggestions are not active. Future integrations should fit an extensible shared source contract. This does not imply implementing every future connector in the initial release, importing every entity automatically, or allowing recorded data to actuate equipment. Entity selection and ingestion/retention cadence remain for architecture.

### Owner decision: Home Assistant ecosystem-first capability fit

Across product workflows, first assess Home Assistant's native capabilities and suitable capabilities available through its ecosystem before building equivalent custom functionality. If reuse materially simplifies the product, propose requirement changes for the owner's approval rather than treating existing requirements as immutable. Evaluate a plugin's compatibility, maintenance, semantics, and whether it would become a required dependency; do not install or make a plugin mandatory solely because it exists.

### Owner decision: initial language, units, and preference scope

The initial release supports Spanish-language presentation and the metric measurement system. Installation-level settings provide defaults, and individual Home Assistant users can override them. Language and unit preferences remain independent; additional languages and measurement systems can be added later.

### Owner decision: TDS monitoring and future digital-twin analysis

Source-water TDS remains an independent measurement for tracking source-water/treatment output over time. Reuse a suitable Home Assistant sensor and native history/presentation when available; retain manual capture and add no parallel monitoring surface unless HA cannot preserve the needed context. Do not use TDS with a lot ICP report to infer prepared-water chemistry in the initial release. Later digital-twin work may consider evidence-based inferences or predictions, including such estimates, only through a separately decided and validated capability that keeps derived results distinct from measurements.

### Owner decision: batch use traceability

When prepared saltwater is transferred for a water change, record each amount transferred and destination Tank in a linked Water Change Record. One batch may support multiple transfers and different Tanks. This narrow flow is in the initial release; a general aquarium-event or inventory system is not implied. Any remaining-volume display must disclose that it is calculated from recorded transfers and may not account for unrecorded losses or uses.

### Owner decision: freshwater/saltwater storage, top-offs, and discards

Freshwater and saltwater can be held in Storage Containers and used for Tank top-offs. Containers are graduated and are recorded through periodic direct level/volume observations; consumption or top-off amounts may be derived by comparing a current observation with the preceding observation and known intervening records. Direct observations and calculated quantities remain distinct. Discards must be recorded and kept separate from water transferred to a Tank.

The initial release does not require an ATO integration. Manual top-off recording remains available. A future ATO source may be incorporated only when its provenance and volume semantics are clear; an ATO status signal alone is not an exact volume.

A Storage Container may receive water from multiple source batches of the same water type, including multiple RODI batches. Freshwater and saltwater must not be combined in one contents cycle. Before changing the container to another water type, account for the previous contents and begin a new cycle. Link each contribution to its known source and amount when available. Derive consumption or top-off amounts by comparing a current level with the preceding level and known intervening records; keep the direct observation distinct from the derived value. Do not report exact remaining source proportions or composition when contribution amounts or intervening history are incomplete.

### Owner decision: separate trend series

Show manufacturer lot ICP results and direct measurements of prepared batches and aquarium water as distinct, traceable trend series. Do not present them as interchangeable or overlay them when their units/context do not support comparison. Prepared-batch chemical estimates are not included in the initial release. Basic trend views are proposed for the initial release; detailed chart design remains for UX work.

Use the analysis date for lot ICP points and measurement time for direct measurements. Preserve report issue/recording times separately and do not invent dates that are absent.

### Owner decision: direct measurements of prepared water

Allow actual measurements taken from a prepared batch (for example salinity, alkalinity, calcium, or magnesium), linked to the batch and Sample where applicable. Keep them distinct from lot ICP results. Initial-release chemistry values come from direct measurements or explicitly attributed reports, not estimates.

### Owner decision: aquarium operation records

The initial release must support basic planning and recording of at least dosing, cleaning, and maintenance operations, manually and from a supported Home Assistant automation/source where available. Keep planned and completed operations distinct; recording completion retains the actual occurrence time and does not imply that a planned action occurred. Generate alerts and reminders for planned operations by adapting to Home Assistant notification services available natively or through installed plugins/extensions, reusing existing user settings where possible and without executing the operation. Timing and overdue/repetition behavior defer to the selected capability; recurring operation schedules are not included in this basic planning decision. Keep these dated Aquarium Events distinct from measurements and never imply equipment actuation or an unobserved result. More operation types and per-type detail remain open.

Each dosing record identifies the product, quantity, and unit, links to the product lot when known, and specifies where the product was added (for example, directly to a Tank or into a prepared-water batch). Keep the dosing destination distinct from a physical Domain Location. This does not imply full inventory management.

Each cleaning or maintenance record identifies the affected equipment/component and the action performed.

When it replaces a consumable, the record includes the product, quantity/unit, and product lot when known; no general stock ledger is implied.

### Owner decision: manufacturer ICP retrieval

Manual source-linking, report-file attachment, and transcription of all reported ICP analytes are supported forms and may be combined for a lot's manufacturer ICP report in the core product. Transcribed results belong to the salt lot/report, not the aquarium or an actual analysis of the prepared batch. Any Aquaforest-specific automatic retrieval may exist only as an optional plugin/extension; the core workflow must remain usable without it.

## Future digital-twin inference and estimation research (not approved for the initial release)

- Any future estimate would be distinct from a measured analysis of a prepared batch, with its own identity and links to exact inputs and method/version.
- Any future estimate must not replace or override directly measured results.
- Do not assign the measured source-water TDS value to particular ions. The source TDS can describe aggregate dissolved solids/conductivity, while the lot ICP supplies manufacturer-reported chemistry for production samples; any combination needs an explicit, reviewed inference method.
- Match or disclose differences between the manufacturer's report dilution/salinity basis and the owner's actual source volume, salt mass, final volume, and measured final salinity. If necessary inputs are missing or incompatible, do not produce a precise-looking result.
- Retain report qualifiers and limits; do not turn not-detected, below-limit, or rounded report values into exact composition claims.
- A trend can be useful even when approximate, but the UI must identify the result as estimated and retain enough lineage to explain changes in source water, salt product/lot, measured salinity, or method.
- Comparing an estimate to aquarium measurements may help investigate patterns; temporal association alone does not establish that the replacement water caused a tank change.

## Remaining owner decisions

No remaining owner decisions are recorded in this addendum for the storage-container and ATO scope. The initial release uses periodic observations from graduated containers and does not require an ATO integration.

The PRD records the open question of what evidence and acceptance criteria would be required before introducing digital-twin inferences or predictions in a later release. Prepared-water estimate formula, inputs, uncertainty, and report-basis policy are deferred with that decision and are not initial-release requirements.
