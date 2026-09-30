---
title: ha-tank-os Product Requirements Document
status: final
created: 2026-09-30
updated: 2026-09-30
---

## 0. Document Purpose

This document defines the product direction and owner-approved initial release of an open-source aquarium-management module for Home Assistant. It distills the owner's vision in [`docs/vision-y-requisitos.md`](../../../../docs/vision-y-requisitos.md) and the product-owner conversation. Research observations and candidate fields for prepared-water tracking are recorded separately in [`addendum.md`](addendum.md); the external product review is recorded in [`competitive-review.md`](competitive-review.md). Research findings were considered separately and only owner-confirmed outcomes are included as requirements. Remaining open questions are explicitly indexed below and are primarily architecture, operational policy, or future research. Product requirements are stated independently of implementation choices.

## 1. Vision

Aquarium keepers currently spread measurements, equipment status, maintenance notes, and aquarium routines across test-kit notes, spreadsheets, Home Assistant entities, and memory. ha-tank-os brings aquarium-specific records into the Home Assistant environment where users already monitor their systems, while allowing both manual capture and connection to automated data sources.

The product lets an owner understand what was observed, when, where, by which method or source, and how aquarium state changed over time. Manual results and automation-derived telemetry can be viewed and queried together without hiding their different origins or replacing one record with another. Home Assistant supplies useful monitoring and automation context; ha-tank-os supplies the aquarium-specific record keeping that native features do not adequately provide.

The project begins as a personal tool for the owner's aquariums and Veril is its first use case. It is open source and should be understandable and extensible by future contributors, without assuming a hosted service, commercial support, or a broad public-user launch in the first release. The product is intended to evolve from trustworthy recording and history toward events, operational relationships, descriptive analysis, and—only after validation—prediction.

### Product principle: Home Assistant ecosystem first

The product uses Home Assistant core capabilities and suitable installed plugins or extensions as the default starting point for every workflow. It adds custom aquarium-specific behavior only where the existing capability does not provide sufficient value, semantics, traceability, or usability. If an existing solution covers nearly all of a proposed need but leaves a small gap, that gap must be presented to the product owner for review before custom functionality is added. The owner may decide that the remaining gap is unimportant and that the product requirement should be simplified. This principle prevents duplicating mature Home Assistant functionality and keeps custom scope focused on the value that ha-tank-os uniquely provides.

## 2. Target User

### 2.1 Jobs to Be Done

- As an aquarium keeper, I want to enter test results and observations in Home Assistant so that my aquarium records are close to the tools I use to monitor it.
- As an aquarium keeper, I want automated readings and manual measurements available in a coherent history while retaining where each came from, so I can compare them responsibly.
- As an aquarium keeper, I want to review the latest and previous values with their dates, methods, and quality context so I can understand change rather than see only a single number.
- As an aquarium keeper, I want to edit or delete a mistaken entry directly, so I can keep my records accurate without a replacement-record workflow.
- As the project owner, I want a useful personal tool that can be extended by an open-source community without making the first release depend on public hosting or support operations.

### 2.2 Non-Users (Initial Release)

- Users seeking a hosted, multi-tenant aquarium SaaS or a centrally managed account service.
- Users seeking autonomous treatment, dosing, heating, cooling, or other closed-loop control from recorded data.
- Contributors expecting every eventual aquarium-management capability to be complete in the first release.

### 2.3 Initial User Journey

- **UJ-1. Ricardo, the aquarium owner, records and reviews an aquarium measurement.** Ricardo opens the aquarium-management experience in Home Assistant, chooses the relevant tank and measurement context, enters a result (or views an automatically received result), and can later find it alongside related history. The record retains its time, source, unit, and method where known. If Ricardo finds a mistake, he can edit or delete the record directly. **[ASSUMPTION]** The first usable interface is provided within Home Assistant; exact screens and interaction pattern remain for UX/architecture.
- **UJ-2. Ricardo tracks prepared water from storage to aquarium.** Ricardo prepares or refills an identified container with freshwater or saltwater, records the amount or fill level and the source, and later records a manual top-off or water change to one of his aquariums. The system links each transfer to the container or batch and destination, derives consumption from periodic graduated-container observations when the record supports it, and keeps any discard separate from water delivered to a Tank.

## 3. Glossary

- **Tank** — A managed aquarium or aquatic system. Veril is the first intended Tank.
- **Domain Location** — A physical or logical place within or associated with a Tank, such as a display, sump compartment, reservoir, or sample container. It is distinct from a user's geographic location.
- **Sample** — A concrete collected portion of water or other material to which one or more observations may refer.
- **Prepared Water Batch** — A specific amount of water prepared for aquarium use, such as freshwater or saltwater, with its own identity and traceable links to its inputs and records. Salt product, amount, lot, and ICP details apply when the batch is prepared as saltwater.
- **Storage Container** — An individually identifiable vessel that holds aquarium-use water. Its water type and fill/withdrawal history are recorded over time; one vessel may be reused across refill cycles.
- **Water Change Record** — A record of a specific water-change operation for a Tank, including its time and water volume, and links to the prepared-water batch used when known.
- **Top-Off Record** — A record of water added to a Tank to replace evaporative loss, manually or through an automatic top-off (ATO) system, with the water type and source linked when known.
- **Observation** — An attributed reading or result, captured manually or received from an automated source. It may optionally reference a Sample.
- **Provenance** — Information describing where a record came from, including its source, capture/import path, and applicable identifiers.
- **Method** — The procedure or technique used to obtain an Observation.
- **Instrument** — A device used to obtain an Observation, when applicable.
- **Aquarium Event** — A persistent record of something that happened to or around a Tank, distinct from a Home Assistant event-bus message and from an Observation.
- **Canonical record** — The authoritative product record for a domain fact, distinct from a Home Assistant display entity or derived statistic.
- **Display unit system** — A user's selected presentation of compatible quantities; changing it must not silently rewrite the recorded source value or unit.

## 4. Features

### 4.1 Aquarium and Measurement Records

The product records aquarium observations as durable, attributable history rather than overwriting a single current value. Records may be partial and need not contain every possible parameter. **[ASSUMPTION: The initial release's core entities follow the proposed Tank, Domain Location, Method, Instrument, Sample, and Observation model from the vision document.]**

#### FR-1: Identify aquarium and measurement context

The owner can manage multiple Tanks from the initial release and associate each Observation with its Tank and, when relevant, a Domain Location, Sample, Method, and Instrument. A Sample may be shared by multiple Observations from the same collection; an Observation may exist without a Sample. Veril is the first intended Tank, not the only supported Tank.

**Consequences (testable):**

- A record can be retrieved with its linked context and stable identity.
- Records belonging to different Tanks remain distinguishable and can be queried in their Tank context.
- The product does not require a Sample for an Observation when the source has no sample concept, such as periodic sensor telemetry.
- Tank and Domain Location identities do not depend on Home Assistant entity names.

#### FR-2: Capture manual observations

The owner can create a manual Observation for a configured aquarium parameter, including its reported value, unit, and available measurement time and provenance, either as an individual result or grouped with other results from the same measurement session and Sample. Sessions may be partial and preserve each reported result's precision and qualifiers such as `<`, `>`, or not detected when provided. Parameter definitions are configurable rather than restricted to a closed product-wide list.

**Consequences (testable):**

- A manual result is stored as an individual record and does not overwrite earlier results.
- The owner can capture a result on its own or group multiple parameter results from the same session and Sample; neither workflow requires a complete fixed panel.
- The owner can start a configurable test-day capture flow that presents relevant parameters for the Tank's current lifecycle phase without requiring a complete fixed panel.
- Missing source times are not invented; available collection, measurement, report, and recording times remain distinguishable.
- Parameter/unit mismatches are rejected or clearly surfaced rather than silently reinterpreted.
- An Observation remains interpretable against the parameter definition and unit in effect when it was recorded, even if the user later edits their configuration.

#### FR-3: Receive automated measurements and equipment states

The product automatically receives relevant data from entities exposed by Home Assistant, including sensor measurements (such as temperature and humidity) and available readings or state changes from actuators and other aquarium equipment. The owner can associate source entities with the relevant Tank, Domain Location, or equipment either by configuring the association manually or by reviewing and accepting an automatic suggestion. A suggested association is not used until the owner accepts it. The product retains source identity and applicable timestamps and presents automated data alongside manual records. Future integrations must be able to provide data through an extensible source contract without requiring a redesign of the core record model; implementing every possible future connector is not part of the initial release. This capability records and presents data and does not control actuators.

**Consequences (testable):**

- Users can distinguish manual, Home Assistant entity, imported, and calculated origins where known.
- Relevant configured sensor readings and actuator/equipment states exposed by Home Assistant become available without manual re-entry.
- The owner can manually associate an entity with its Tank and, when known, its Domain Location or equipment; the source entity remains traceable.
- Automatic association suggestions can be reviewed and accepted; an unaccepted suggestion does not affect record classification or presentation.
- Future supported integrations can provide data through the shared source contract without changing the meaning of existing manual or Home Assistant-sourced records.
- Repeated or imported data does not silently erase an existing record; conflicts and duplicates have an explicit outcome.
- Availability of a Home Assistant entity does not, by itself, require copying every update into canonical persistence.

#### FR-4: Review latest values and history

The owner can find a Tank's latest chronological observation and its history. When valid observations disagree, the initial release presents the most recent observation as the current value together with its source and context; it does not silently select a preferred value based on source type or method.

Canonical aquarium records do not expire automatically based on age. High-volume Home Assistant telemetry is not copied wholesale into permanent aquarium records by default; the owner can select relevant sources, and suitable Home Assistant history/Recorder capabilities should be reused where they meet the need. Imported telemetry selection, sampling cadence, and retention behavior are defined for the selected sources.

**Consequences (testable):**

- A displayed value can be traced to the Observation and its timestamp, source, and unit.
- A stale value remains distinguishable from an invalid value.
- Historical records remain individually accessible even when Home Assistant also presents a current-state projection or aggregate statistic.
- Chemical values shown for aquarium water and prepared-water batches are direct measurements or explicitly attributed source-reported results; the initial release does not substitute inferred chemical contribution estimates.

#### FR-17: Review distinct chemistry trends

The owner can review trends for source-water TDS observations, manufacturer ICP results associated with salt lots, and direct measurements of prepared-water batches and aquarium water. These are presented as distinct, explicitly attributed series with links to their underlying source records. Basic trend views can show target bands from the applicable Tank parameter and lifecycle-phase profile, and can mark recorded water-change events when the context is meaningful. A chart may overlay series only when their parameter, units, and contexts support a meaningful comparison; the product must not imply that a lot analysis and a water measurement are the same kind of sample or observation. Source-water TDS is monitored as an aggregate water-quality reading, not an ion-specific analysis. Use Home Assistant history, statistics, and presentation where they preserve the required attribution and context; add only missing aquarium-specific views. Plot ICP results at their analysis date and direct measurements at their measurement time. Preserve distinct report issue, recording, and other applicable timestamps, and never invent a missing time.

**Consequences (testable):**

- The owner can review source-water TDS history and distinguish it from lot-report results and direct measurements of prepared water and aquarium water.
- A direct aquarium measurement is not replaced or hidden by a lot result.
- ICP results and direct measurements use their respective analysis and measurement dates as the trend time; missing dates are not fabricated.
- Units or contexts that cannot be meaningfully compared are shown separately or are not overlaid, with the reason made clear.
- Selecting a plotted point opens or identifies the underlying source record and its provenance.
- Target bands identify the applicable Tank/profile context and are not presented as universal aquarium standards.
- Water-change markers identify recorded events and do not imply that a measured change was caused by that event.

#### FR-18: Record direct measurements of prepared water

The owner can record actual measurements taken from a specific Prepared Water Batch, including salinity and any other configured water-quality parameters such as alkalinity, calcium, or magnesium. Each result is linked to the batch and, when applicable, a Sample, measurement time, Method, Instrument, source unit, precision, and qualifiers. A direct measurement describes the sampled prepared water and is distinct from the manufacturer's salt-lot ICP analysis. The initial release does not derive estimated chemical composition from lot data or source-water TDS.

**Consequences (testable):**

- Multiple measured parameters from the same prepared-water sample can be linked to the same Sample and Prepared Water Batch.
- Prepared-water chemical values are presented only as direct measurements or explicitly attributed manufacturer/report results, not as inferred batch chemistry.
- A prepared-water measurement is not presented as a measurement of the aquarium Tank.
- Measurements retain source values, units, qualifiers, and provenance and remain available for history/trend review.

#### FR-19: Record aquarium operations

The owner can plan and record aquarium actions, including dosing, cleaning, and maintenance, as distinct Aquarium Events associated with the relevant Tank. A planned operation is distinguishable from an action that actually occurred. When it is carried out, the owner can record its actual occurrence without losing the planned date or presenting the plan as evidence that the action happened. The product can generate alerts and reminders for planned operations by adapting to notification services available natively in Home Assistant or through installed plugins/extensions. It should reuse the user's existing notification channels and settings where possible rather than introduce a parallel notification system. Notifications never execute the planned operation. Records may be entered manually or received from a relevant Home Assistant automation/source when available, while preserving provenance. They may include a Domain Location, product or equipment, quantity and unit where relevant, and notes. An operation record is not itself a measurement or proof of an unobserved physical result.

**Consequences (testable):**

- Dosing, cleaning, and maintenance actions can be recorded and retrieved by Tank and time.
- Planned operations are distinguishable from completed operations; recording completion preserves the actual occurrence time and does not erase the planned time.
- Alerts and reminders adapt to Home Assistant's native notification services or installed plugins/extensions and reuse their available channel/settings where possible; they never perform or initiate the planned action.
- Manual and automation-sourced events remain distinguishable and link to their originating input where known.
- Every dosing record identifies the product added, the quantity, and its unit, links to the product lot when known, and identifies where it was added (for example, directly to a Tank or into a prepared-water batch). The record retains the related Tank and distinguishes the dosing destination from the physical Domain Location when both are known. This does not require full stock or inventory management.
- Every cleaning or maintenance record identifies the affected equipment/component and the action performed.
- When a cleaning or maintenance action replaces a consumable, the record identifies the replacement product and quantity/unit, and links to its product lot when known. This does not require general stock/inventory management.
- Other quantities, equipment, locations, and notes can be attached when relevant without requiring every event type to have the same fields.
- Related Observations can be reviewed near an event in history without being merged into or inferred from the event.
- Recording an event does not itself actuate equipment or assert an unverified physical outcome.

#### FR-20: Configure process-capture fields

For each supported process type, the owner can configure which available context fields are requested and recorded, using both selectable built-in fields and owner-defined custom fields. The owner can mark configurable fields as required or optional for that process type. This applies across supported processes, including water preparation, measurement sessions, top-offs, dosing, cleaning, and maintenance. Required identity, time, source, destination, and relationship data needed for a record's meaning and traceability cannot be disabled. Custom fields support text, numbers with optional units, yes/no values, and predefined choices. A required field can be completed with an actual value or an explicit unknown/not-measured state; this state is distinct from an empty field and from a numeric zero. When a field is marked unknown/not measured, the owner may optionally record a reason.

**Consequences (testable):**

- Optional fields can be enabled or disabled per supported process type.
- Each configurable field can be marked required or optional for its process type.
- A process record cannot be completed while a configured required field is empty; it can be completed when each such field has a value or an explicit unknown/not-measured state.
- Unknown/not-measured is stored and displayed distinctly from empty and zero, and is never treated as a measurement or inferred value.
- An optional reason can be recorded with an unknown/not-measured value; the reason is not required to complete the process record.
- Process configuration changes do not delete historical values or silently change the meaning of existing records.
- Preparation temperature, mixing duration, and mixing procedure are available as optional configurable context, not mandatory fields for every batch.
- Owners can define custom context fields in addition to enabling/disabling built-in optional fields.
- Custom field definitions and their values remain interpretable in historical records after a configuration change.

#### FR-21: Provide transparent aquarium calculators

The owner can use calculators for water-change volume, compatible unit conversion, and graduated-container volume or change calculations where the required inputs exist. Calculators show their inputs, units, assumptions, and whether the result is direct or derived. A calculated result does not replace or alter the underlying records and is not presented as a measurement.

**Consequences (testable):**

- A calculator identifies every input and unit used in its result.
- Derived volume results identify the calculation basis and any missing or uncertain inputs.
- Unit conversion does not change the stored source value, source unit, precision, or provenance.
- A calculator never turns an estimated or incomplete result into a verified measurement.

#### FR-5: Edit and delete records directly

The owner can edit or delete a record directly without requiring a linked replacement record. Deletion removes the record from the product's active records. The product must not silently delete dependent records: when dependencies prevent deletion, the owner must resolve those relationships before deleting the target. Existing backups may retain deleted records, and restoring an older backup may reintroduce them; backup rotation and recovery behavior remain for architecture and data-lifecycle design.

**Consequences (testable):**

- The owner can update a record's editable values directly, and subsequent views show the edited values.
- The owner can delete a record directly, and it no longer appears as an active record.
- Editing one record does not silently alter unrelated records or their provenance.
- Deleting a record does not silently delete dependent records; deletion is blocked while unresolved dependencies remain.

#### FR-10: Configure aquarium parameters and use templates

The owner can configure which parameters are relevant to each Tank instead of being limited to a fixed catalog. The product provides editable starter templates for aquarium types, including freshwater and marine, so a Tank can begin with a relevant set of parameters. Initial lifecycle phases are cycling, maturation, and established operation. The owner can add and modify phases and their associated measurement profiles, identify the current phase, and change it as the Tank progresses. Templates and profiles are starting points, not restrictions; users can add, remove, or adapt parameters without making existing Observations uninterpretable. No single target value or parameter set is presumed universal.

**Consequences (testable):**

- A user can configure a parameter beyond the built-in starter sets and record Observations for it.
- Starter templates can be selected and then customized without changing another Tank's configuration unless the owner explicitly applies that change.
- The owner can associate different measurement profiles with configured lifecycle phases and identify the current phase for a Tank.
- The initial phase list includes cycling, maturation, and established operation; the owner can add and modify phases and their profiles.
- Changing the current phase changes which profile is presented for new measurements without rewriting or reclassifying historical Observations.
- Historical Observations retain the phase context recorded when they were captured when a phase or profile is later modified.
- Changes to a parameter's label, unit, or configuration do not silently rewrite historical source values or their meaning.
- Variable analytes in laboratory reports, including ICP/ICP-OES, are not rejected solely because they are absent from a fixed built-in list.

#### FR-11: Do not estimate prepared-water chemical contributions in the initial release

The initial release does not calculate or present estimates of prepared-water chemical contributions by combining source-water TDS with manufacturer salt-lot ICP data or other declared product composition. It may record and present source measurements, direct prepared-water measurements, and manufacturer reports as separate, attributed records. Later digital-twin capabilities may add evidence-based inferences or predictions, but each requires a separate product decision, validation, and clear distinction from measurements. This restriction does not prohibit arithmetic volume calculations based on recorded container levels, additions, transfers, and discards.

**Consequences (testable):**

- Source-water TDS, manufacturer lot-analysis values, and direct prepared-water measurements remain distinct and retain their own provenance.
- No estimated chemical contribution is generated from source-water TDS and lot-analysis data in the initial release.
- Volume arithmetic based on recorded additions, levels, transfers, or discards remains distinct from a water-quality measurement or chemical estimate.

#### FR-12: Trace each prepared-water batch

The owner can record each freshwater or saltwater preparation as an individually identifiable Prepared Water Batch. Record source-water volume and link to its independent TDS Observation when available. TDS observations can also be recorded and reviewed over time to monitor source-water treatment output, independently of any batch estimate. Use an existing Home Assistant sensor/history when available and semantically suitable, while retaining manual entry. For saltwater, also record salt product/type, quantity, and specific lot, and link to the lot's manufacturer ICP analysis when available. The owner can record final measured salinity and its measurement context. No additional preparation-context field is mandatory by default; the owner configures any additional data, such as temperature, mixing duration, or procedure, through process-capture settings. A batch without a final salinity measurement remains usable, but the product warns that it has not been checked and does not present it as verified. The batch and linked evidence remain associated for traceability and review.

**Consequences (testable):**

- Two preparations using different source readings or salt lots can be distinguished and reviewed independently.
- Source-water TDS readings remain independently identifiable and reviewable over time; a Prepared Water Batch links to its relevant TDS reading when available, and missing links are shown rather than inferred.
- The batch records whether its contents are freshwater or saltwater; salt product, salt quantity, and lot are associated when salt was used.
- The recorded source-water volume, TDS when available, salt type/product, salt quantity, and lot remain associated with the specific Prepared Water Batch as applicable.
- Final salinity can be recorded for saltwater with its unit, measurement time, temperature, and instrument/method when known.
- Missing final salinity does not block the owner from using the batch, but the product displays a clear warning and never labels the batch as salinity-checked or verified.
- No extra preparation-context fields are imposed as universal requirements; the owner can configure them as required or optional for water preparation.
- Missing direct measurements are shown as not recorded rather than inferred; the absence of a chemical estimate does not prevent use or traceability of the prepared-water batch.
- A later correction to source information does not silently rewrite the historical batch record or erase its prior provenance.

#### FR-13: Trace prepared-batch use in water changes

When the owner uses prepared saltwater for a water change, the owner can record each amount transferred and the destination Tank in a Water Change Record linked to the Prepared Water Batch. One batch can have multiple transfers, including transfers to different Tanks. The record distinguishes the volume prepared from each amount transferred and from any aquarium water removed or replaced. This is a narrow first-release operation needed to preserve the stated batch-to-aquarium traceability; it does not require a general event or inventory-management system.

**Consequences (testable):**

- A prepared batch can be traced to the Water Change Record and Tank that received its water.
- One Prepared Water Batch can be linked to multiple Water Change Records and destination Tanks.
- The amount transferred from a batch is distinguishable from source-water volume and from removed/replaced aquarium-water volume.
- Any displayed remaining volume is derived only from recorded preparation volume and recorded transfers/adjustments; it is not presented as exact if unrecorded losses or uses may have occurred.
- The batch, transfer, and water-change history remain queryable together over time.

#### FR-14: Track storage-container refills, levels, and discards

The owner can identify a Storage Container and record its freshwater or saltwater contents, refills, observed fill levels or volumes, withdrawals, and discarded water. Each contents cycle has one water type; freshwater and saltwater must not be combined in the same cycle. Before changing the container to a different water type, the previous contents must be accounted for and the new contents cycle started. Contents may receive contributions from multiple source batches of the same water type, including multiple RODI batches, and each contribution can link to its source and amount when known. Containers are graduated, so the initial release records periodic direct level/volume observations. A consumption or remaining-volume value may be derived by comparing a current observation with the preceding observation and accounting for known intervening refills, withdrawals, and discards. A direct level observation is never conflated with the derived value. Discarded volume is recorded so it is not mistaken for aquarium use. Composition or source proportions are not presented as exact when contribution amounts or intervening history are incomplete.

**Consequences (testable):**

- A Storage Container can be reused across refill cycles, and each cycle records its water type and known source batch or source; one contents cycle can receive contributions from multiple source batches.
- A single contents cycle cannot combine freshwater and saltwater; changing water type requires accounting for the previous contents and starting a new cycle.
- Each known contribution to container contents retains its source batch/source and amount when known, without implying exact source proportions when amounts or history are incomplete.
- A user can record a refill and its resulting level/volume, or a subsequent observed level/volume, to support a derived consumption estimate.
- The owner can enter the volume added or the current volume remaining in marked units such as litres, without those two meanings being conflated.
- Consumption calculated from successive current-level observations remains distinguishable from a directly entered added or transferred amount.
- Directly measured, automatically reported, manually observed, and calculated volumes remain distinguishable.
- The owner can record water discarded from a batch or Storage Container, and that amount is not counted as transferred to a Tank.
- A displayed remaining or consumed volume is not presented as exact if container calibration, intervening refills, withdrawals, or discards are incomplete.

#### FR-15: Trace evaporation top-offs

The owner can record each top-off to a Tank manually, identifying whether freshwater or saltwater was added and linking the source Storage Container or Prepared Water Batch when known. The initial release does not require an ATO integration; periodic graduated-container level observations remain the supported basis for deriving an amount when the record is sufficient. A future ATO source may be incorporated only if its provenance and volume semantics are clear. An ATO signal or status alone is not represented as an exact water volume.

**Consequences (testable):**

- A top-off is distinguishable from a water change and is linked to its destination Tank and water source when known.
- Manual, ATO-reported, and level-derived quantities preserve their different provenance and precision.
- A missing ATO integration or ATO volume signal does not prevent the owner from recording a top-off manually.
- When ATO events or readings are available, they retain their source and are not silently duplicated by a manual record for the same event.
- The water type (freshwater or saltwater) is explicit; the system does not infer it from the container name or ATO label.
- Logging a top-off does not itself command an ATO or other equipment.

#### FR-16: Associate manufacturer lot analyses

The owner can associate a manufacturer's ICP report with the exact salt product lot used in a Prepared Water Batch through one or more supported manual forms, including a source link, an attached report file, and transcribed results. These forms can be combined while retaining their relationship to the same report and lot. The owner can transcribe every analyte reported, including analytes absent from built-in or Tank-specific parameter templates. Preserve the report's analyte names, values, source units, qualifiers, and stated limits/context where available. Lot-analysis results remain attributed to the salt lot and report; they are not observations of the aquarium or direct measurements of the owner's prepared batch. If the report is unavailable, the product records that it is missing and does not silently invent or substitute lot results. Manual association and transcription are part of the core product. Any Aquaforest-specific automatic report retrieval must be delivered, if feasible, as an optional plugin/extension; it must not be a core dependency or required external account/service.

**Consequences (testable):**

- A report and any transcribed results are linked to the salt product lot, not merely to a product brand or aquarium.
- The owner can use a source link, attach the report file, transcribe results, or combine these forms for the same lot report.
- Every reported ICP analyte can be transcribed, including analytes not present in a built-in catalog or Tank template.
- Transcribed lot-analysis values preserve source names, units, qualifiers, and stated limits/context when available, and remain distinct from aquarium and prepared-water Observations.
- The product preserves the report source and its own analyte values, units, qualifiers, and preparation basis when available.
- Missing reports remain explicitly missing and are never substituted with inferred chemistry values.
- Core manual lot/report workflows remain usable when the optional manufacturer plugin is absent, unavailable, or fails.

### 4.2 Home Assistant Experience and Safety

The product belongs in the Home Assistant environment and should reuse native capabilities or suitable capabilities from its ecosystem when they satisfy the need. It must add only aquarium-specific functionality that is missing. Review capability fit across product workflows, including capture, presentation, history, notifications, and integrations. A fit review may recommend simplifying or changing a requirement, but only the product owner can approve that change. Home Assistant entities are useful projections, not one entity per historical record and not automatically the canonical archive.

#### FR-6: Present aquarium information in Home Assistant

The owner can access the product's essential setup and aquarium information through Home Assistant's native experience or a suitable installed ecosystem capability, and can expose useful current values there without confusing projections with the underlying records. Custom product UI is added only for requirements not adequately met by the selected capabilities.

**Consequences (testable):**

- A current-state projection can be reconstructed from canonical records after Home Assistant restarts, subject to defined persistence availability behavior.
- The product does not create an unbounded set of Home Assistant entities for historical rows.
- The product clearly communicates relevant unavailable, stale, or invalid states rather than presenting them as current valid measurements.
- Product workflows reuse a native or selected ecosystem capability when it meets the workflow's data, traceability, and usability requirements; identified gaps are handled without duplicating the capability that already works.
- Optional plugins are not silently treated as required dependencies; any required capability and its dependency/maintenance implications are explicit.

#### FR-7: Prevent recording from causing physical actions

Creating, importing, correcting, or viewing an Observation or Aquarium Event does not by itself trigger dosing, heating, cooling, or another physical action. Any future control capability requires a separate explicit product decision, permissions, safeguards, and validation.

**Consequences (testable):**

- Record operations have no implicit equipment-control side effects.
- A future action feature cannot be inferred from the existence of an automation source or threshold.

### 4.3 Portability and Inclusive Product Use

#### FR-8: Preserve and exchange records

The owner can export and restore or import records in a way that preserves stable identities, relationships, provenance, original values and units, qualifiers, and timestamps. **[ASSUMPTION: A usable export/import path is in the initial release because the vision's proposed first vertical slice uses it to validate data portability.]**

**Consequences (testable):**

- A round-trip preserves semantic meaning and relationships.
- Import conflicts or duplicates have an explicit, non-destructive outcome.
- Backup/recovery behavior is documented for the selected storage mechanism.

#### FR-9: Support languages, locations, and measurement systems

The initial release provides Spanish-language presentation and the metric measurement system, with architecture that allows additional languages and measurement systems to be added. Installation-level language and unit settings provide defaults; each Home Assistant user can override those preferences without changing another user's presentation. Language, locale, time zone, geographic location, and unit preferences remain distinct. Users can view compatible quantities in supported measurement systems without losing the recorded source value, unit, precision, qualifiers, or provenance.

**Consequences (testable):**

- Language/locale changes affect presentation, not stored domain meaning or record timestamps.
- Spanish and metric units are available in the initial release.
- Installation defaults apply when a user has no override; one user's language or unit override does not change another user's presentation.
- Missing translations use a defined fallback without changing domain data.
- Conversions are explicit and traceable; unsupported or incompatible quantities are not silently converted.
- The product can represent multiple user, tank, and operational geographic locations independently of Domain Location.

The initial supported language and measurement system are Spanish and metric. Installation settings provide defaults, with optional per-user overrides. Additional languages and measurement systems remain part of the product's multilingual, multi-location, and multi-unit design.

## 5. Non-Goals (Explicit)

- Hosted multi-tenant service, account system, monetization, or commercial support commitment in the initial release.
- Autonomous dosing, heating, cooling, or other equipment control based solely on recorded or derived data.
- A validated predictive model in the initial release. Prediction is a later capability and must be evaluated against real observations before it informs control.
- Replacing every Home Assistant recorder, history, statistics, automation, dashboard, or notification feature.
- Treating Veril-specific helpers or configuration as the product's permanent domain boundary.

## 6. Initial Release Scope

This is the owner-approved product boundary for the initial release. Technical feasibility, Home Assistant capability fit, and architecture still require separate validation.

### 6.1 In Scope

- Core Tank, Domain Location, Sample, Observation, Method, and Instrument concepts as needed for reliable records.
- Management of multiple Tanks from the initial release, with Veril as the first intended use case.
- Configurable per-Tank measurement parameters and editable freshwater and marine starter templates. **[ASSUMPTION: both starter templates ship in the initial release.]**
- Individually identifiable, traceable records for each prepared replacement-water batch. **[ASSUMPTION: this capability is included in the initial release to support the stated use case.]**
- Independent, traceable source-water TDS monitoring and history, reusing suitable Home Assistant measurements/history when available.
- Direct measurement and traceability of prepared-water quality; no chemical contribution estimate from source-water TDS and lot ICP data in the initial release.
- A narrow Water Change Record that records the amount transferred from a Prepared Water Batch and the destination Tank.
- Storage Container records for freshwater and saltwater, including refills, levels, withdrawals, and discards, plus manual and supported ATO top-off records for a Tank.
- Manual attachment or source-linking of a manufacturer ICP report to a salt product lot. Manufacturer-specific automatic retrieval is optional and isolated from the core product.
- Manual transcription of all analytes in a lot ICP report, including analytes not already present in parameter templates.
- Manual recording of configured direct water-quality measurements taken from prepared-water batches, distinct from manufacturer lot analyses.
- Basic trend/history views for source-water TDS, lot ICP results, and direct measurements of prepared batches and aquarium water, keeping them distinct and traceable. Reuse Home Assistant history/presentation where it preserves the required meaning; add only missing views. **[ASSUMPTION: this limited trend view is part of the initial release; advanced analytics remain deferred.]**
- Configurable test-day capture for relevant parameters in the Tank's current lifecycle phase, without requiring a complete fixed panel.
- Basic trend target bands tied to the applicable Tank/profile context and recorded water-change event markers.
- Transparent water-change, unit-conversion, and graduated-container volume calculators with direct-versus-derived results clearly distinguished.
- Manual and supported automation-sourced Aquarium Events for at least dosing, cleaning, and maintenance.
- Basic planning of those operations, with planned and completed states kept distinct.
- Configurable optional capture fields for supported process types, including selectable built-ins and owner-defined custom fields, with mandatory traceability data protected.
- Alerts and reminders for planned operations adapted to native Home Assistant notification services or installed plugins/extensions, reusing existing settings where possible.
- Manual creation of aquarium measurements and partial sessions.
- A useful initial path for relevant automated Home Assistant data, while keeping the common manual/automated model and provenance.
- Automatic ingestion of owner-associated Home Assistant sensor readings and available actuator/equipment states; a shared source contract keeps later integrations extensible without requiring every future connector in V1.
- Latest/history retrieval and a Home Assistant presentation of useful current values.
- Direct editing/deletion of records, with deletion blocked rather than cascading silently when dependent records remain.
- Export/import or equivalent owner-controlled portability, with semantic preservation.
- Initial Spanish-language and metric presentation, with installation defaults and per-user overrides; architecture allows additional languages and measurement systems.
- Personal single-owner use, with no hosted service requirement.

### 6.2 Out of Scope for Initial Release

- Complex operation and inventory management beyond the water-change, storage-container, discard, top-off, and basic dosing/cleaning/maintenance records required by FR-13–FR-15 and FR-19.
- Full product, lot, and material inventory beyond traceability of water batches and their recorded transfers.
- Temporal livestock management, automated laboratory report parsing/import, broad external connectors, and full workflows for other laboratory report types. Any Aquaforest retrieval is an optional plugin/extension, subject to feasibility and source availability; manual transcription of all salt-lot ICP analytes is in scope.
- Recurring operation schedules, advanced analytics, validated prediction, or prediction-based automation.
- Estimates of prepared-water chemical contributions derived from source-water TDS, manufacturer lot ICP, or other declared product composition, deferred until a separate product decision and supporting evidence exist.
- User-defined inference formulas or a comprehensive analysis engine.
- Any product or data relationship with the separate TankOS project, including migration, interoperability, or a runtime dependency.
- Livestock/plant tracking, opaque health or stability scores, AI advice/chat/photo interpretation, community features, and public tank comparison are deferred to a future near-term product review; they are not initial-release requirements.
- Automatic manufacturer ICP report parsing is a future near-term optional importer/plugin; manual association and transcription remain the initial-release path.
- Final decisions on all supported integrations, persistence technology, UI architecture, HA version policy, and storage lifecycle; these belong in architecture and ADRs after product scope approval.

## 7. Success Metrics

For this personal-first product, success is initially judged by sustained usefulness and data trust, not adoption or revenue.

- **SM-1 — Personal usefulness:** the owner can use the product to record and review aquarium and prepared-water measurements, water preparations, operations, transfers, and trends as part of their normal Home Assistant workflow over a sustained trial, without reverting to an unlinked parallel record as the only usable history. Validates FR-1–FR-6 and FR-11–FR-19.
- **SM-2 — Record trust:** representative manual and automated records, prepared-water batches and direct measurements, operations, transfers, ICP reports, transcribed analytes, and top-offs can be traced to their source, time, unit, and applicable method/context; direct edits do not alter unrelated records, and deletion does not silently remove dependent records. Validates FR-2–FR-5, FR-8, and FR-11–FR-19.
- **SM-3 — Safe behavior:** record capture, correction, import, and presentation cause no equipment actuation. Validates FR-7.
- **Counter-metric SM-C1 — Feature breadth:** do not optimize for the number of parameters, integrations, screens, or entities at the expense of trustworthy records, understandable setup, and maintainability.
- **Counter-metric SM-C2 — Automation volume:** do not optimize for ingesting every sensor update if that creates duplicate/noisy records or obscures useful history.

The initial personal trial lasts several weeks; the owner judges whether the product is useful based on sustained use of the core recording and review workflows. No usage telemetry or third-party analytics are assumed.

## 8. Cross-Cutting Requirements and Guardrails

- **Data integrity and provenance:** preserve the recorded source, units, precision, qualifiers, methods, instruments, timestamps, and relationships for active records. Direct edits affect only the selected record and are not propagated silently to related records. Quality and freshness remain distinct from record lifecycle. Any future digital-twin inference or prediction must be identifiable as derived, traceable to its evidence and method/model, and evaluated against observations.
- **Ecosystem reuse:** assess native Home Assistant and suitable installed ecosystem capabilities before building equivalent custom functionality. Document capability gaps and plugin compatibility/maintenance tradeoffs; changes to product requirements require owner approval.
- **Persistence and recovery:** canonical aquarium records do not expire automatically and must remain available across Home Assistant restart and be exportable/backed up. Existing backups may retain deleted records, and restoring an older backup may reintroduce them. The storage mechanism, migration, backup rotation, and recovery objectives remain architecture decisions.
- **Safety:** recording or deriving data must not cause physical action. Future action capabilities require separate approval and safety design.
- **Privacy and security:** initial use is local and personal. Access rules for read, capture, correction, invalidation, deletion, and configuration must be defined; credentials and secrets are not aquarium records and must not be exported as such. No cloud processing or analytics is assumed.
- **Usability and accessibility:** common capture/review tasks should be understandable within the Home Assistant context. Specific accessibility target and interaction details remain to be set during UX/design.
- **Localization and quantities:** user-facing copy is localizable; date, time, number, and unit presentation respects configured locale/time zone without changing canonical timestamps or values.
- **Open-source extensibility:** repository-level contribution and cross-platform developer practices support future contributors. The initial product should avoid making the owner's machine or private aquarium setup a runtime dependency.
- **Performance and scale:** the first release should remain usable for a personal aquarium history and modest local sensor inputs. Numeric latency, tank-count, record-volume, and high-volume telemetry retention targets are not yet established and must be validated before architecture finalization.

## 9. Open Questions

1. After reviewing native Home Assistant and selected ecosystem capabilities, which user workflows still require custom interface or behavior?
2. What are acceptable record-volume, backup-rotation, and recovery expectations for a personal installation?
3. Which Home Assistant telemetry sources should be imported, at what cadence, and when should native history/Recorder be used instead of permanent domain records?
4. How should the product communicate that older backups may still contain deleted records and that restoring one may reintroduce them?
5. What must happen when canonical persistence is unavailable during startup or a write?
6. What Home Assistant versions and installation modes will be supported initially?
7. What evidence and acceptance criteria would be required before introducing digital-twin inferences or predictions, including any prepared-water chemical contribution estimate, in a later release?

## 10. Assumptions Index

- **A-1 (§1, §2):** The initial product is primarily for Ricardo's personal aquarium management, with Veril as its first use case; future contributors are a design consideration, not a first-release support obligation.
- **A-2 (§2.3):** The core product experience is accessed from Home Assistant.
- **A-3 (§4.1):** The proposed core data concepts in the vision are appropriate for the PRD's first release, subject to architecture validation.
- **A-6 (§4.3 FR-8, §6):** Export/import is part of the first release because it validates portability and recovery concerns from the proposed vertical slice.
- **A-8 (§6):** General Aquarium Events and complex operations may be deferred from the first release; FR-13–FR-15 and FR-19 define the confirmed narrow water-change, container, discard, top-off, dosing, cleaning, and maintenance flows.
- **A-9 (§8):** Initial product use is local, personal, and does not require cloud services or analytics.
- **A-10 (§7):** The owner's sustained use and trustworthy records are more meaningful initial success measures than community adoption metrics.
- **A-11 (§6):** Editable freshwater and marine parameter templates are both included in the initial release; the parameter catalog remains configurable and is never a closed list. Technical template shape remains for architecture/design.
- **A-12 (§6):** Individually identifiable, traceable records for freshwater and saltwater batches and their water-storage/transfer flows are included in the initial release; additional optional fields and calculation details remain open for architecture/design.
- **A-13 (§6):** Basic history/trend views for source-water TDS, lot ICP results, and direct measurements of prepared batches and aquarium water are included in the initial release; reuse suitable Home Assistant presentation and defer detailed visualization to UX design.
- **A-14 (§4.1 FR-19, §6):** Initial-release operation planning covers one-off planned-versus-completed records and alerts/reminders that adapt to native Home Assistant notification services or installed plugins/extensions. Reminder timing and overdue/repetition behavior defer to the selected capability; recurring operation schedules remain out of scope.
- **A-15 (§4.1 FR-14–FR-15, §6):** Storage containers are graduated and are measured through periodic direct level/volume observations. Initial-release consumption or top-off amounts may be derived by comparison with the preceding observation and known intervening records. No ATO integration is required in the initial release; manual recording remains available.
- **A-16 (§4.1 FR-19, §6):** The initial release starts with dosing, cleaning, and maintenance operations only; additional operation types are deferred.
- **A-17 (§4.1 FR-4, §7, §9):** When valid measurements disagree, the product shows the most recent observation with its source and context rather than selecting a hidden preferred value. The owner's personal trial lasts several weeks.
- **A-18 (§1, §5, §9):** ha-tank-os has no product or data relationship with the separate TankOS project. It may replace that project in practice, but no migration, dependency, or interoperability is part of this PRD.
- **A-19 (§4.1 FR-2, FR-17, FR-21, §6):** The owner approved configurable test-day capture, contextual target bands and water-change markers, and transparent water-change/unit/volume calculators for the initial release.
- **A-20 (§5, §6):** Livestock/plant tracking, scores, AI, community features, and automatic ICP parsing are excluded from the initial release but are candidates for a future near-term review. Device-control schedules remain subject to a separate safety decision.
