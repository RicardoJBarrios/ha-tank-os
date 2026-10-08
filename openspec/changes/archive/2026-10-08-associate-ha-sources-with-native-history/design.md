# Design

## Context

The integration currently has one Home Assistant Config Entry, a config flow without an options flow, and canonical Tank/Domain Location records in `CanonicalRepository`. Tank and location IDs are stable product identities. The adopted architecture assigns integration configuration and source associations to Config Entries while canonical aquarium records remain in the repository (AD-19). See `proposal.md` and `specs/ha-source-associations/spec.md` for the scope and behavior.

## Goals / Non-Goals

**Goals:**

- Configure entity-to-aquarium-context associations with native Home Assistant configuration controls.
- Keep associations separate from canonical aquarium observations.
- Let users rely on Home Assistant's existing entity History/Recorder surface for continuous history.

**Non-Goals:**

- Importing entity states into canonical TankOS observations, sampling, or changing Recorder configuration.
- Generating association suggestions.
- Associating entities with equipment before the product has a canonical equipment target model.
- Building a TankOS history screen or changing Home Assistant's native History UI.

## Decisions

### Store association configuration in the Config Entry options

Store each association as the selected Home Assistant `entity_id`, target type (`tank` or `location`), and the target's stable product ID in Config Entry options. Resolve target labels from the canonical repository when presenting the options flow; never copy Tank or Domain Location records into Config Entry data. This follows AD-19 and avoids turning the HA entity ID into a TankOS domain identity.

**Alternative considered:** store the associations as canonical aquarium records. Rejected because associations are integration configuration, not observations or other permanent aquarium facts.

### Use native Home Assistant selection and target controls

Use a native Home Assistant entity selector for source selection and native selection controls for existing Tank/Domain Location targets. Validate a submitted target ID against the current repository before saving. Do not accept a free-form entity string as an entity selector substitute.

**Alternative considered:** add a custom frontend. Rejected because the selected behavior is configuration and source-history reuse, for which Home Assistant already provides native controls and History UI.

### Treat stale source or target references as unresolved

Resolve saved entity references against current Home Assistant state/registry and targets against the current canonical repository when loading or editing associations. A missing reference remains visible and can be removed or explicitly reassigned by the user. Do not infer a replacement based on labels, entity names, or similar IDs.

**Alternative considered:** silently follow a renamed entity by matching its label or device name. Rejected because names are mutable and may identify a different source.

### Keep continuous history in native Home Assistant History/Recorder

Do not subscribe to entity state-change events or call Recorder internals in this change. Users review an associated entity through Home Assistant's native History surface. History availability, filtering, and retention continue to follow the user's Home Assistant configuration; TankOS does not promise that every entity is recorded or that history survives Recorder purges.

**Alternative considered:** query Recorder from TankOS or mirror each update into TankOS. Deferred because the required data volume, sampling, retention, and in-product presentation policy remain open, and mirroring would create a second history surface.

## Risks / Trade-offs

- [An entity is renamed or removed] → Keep its saved association unresolved until the user selects a replacement; never retarget silently.
- [A Tank or Domain Location is removed while referenced by options] → Show the target as unresolved and require explicit correction or removal; do not mutate other canonical records.
- [Recorder excludes or purges an entity's history] → Native History may be incomplete or empty; document that Recorder configuration governs availability and do not create substitute observations.
- [Associations disappear when the integration entry is removed] → Keep them in Home Assistant configuration and state clearly that they are configuration, not exported canonical aquarium data.

## Migration Plan

No existing association format or imported-telemetry data exists. Add the options flow without changing Config Entry version or existing option data. Confirm setup, options-flow reload, and uninstall behavior with the repository's pinned Home Assistant test environment before delivery.
