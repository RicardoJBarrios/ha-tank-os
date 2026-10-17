# Design

## Context

See `proposal.md` for motivation and `specs/manual-observations/spec.md` for the behavior contract. The application already lists observations by Tank and optional parameter. Native response-capable services are already registered, and observations contain both nullable `measurement_time` and required `recording_time`, plus source and context fields. There is no validity/status field.

## Goals / Non-Goals

**Goals:**
- Add an efficient, deterministic latest-observation projection over the existing observation records.
- Keep the service response compatible with Home Assistant scripts and automations and preserve enough provenance to interpret it.

**Non-Goals:**
- Change canonical storage, observation schema, retention, or the existing list service.
- Add a source precedence policy, validity inference, entity-per-observation model, or custom frontend.

## Decisions

- Add a dedicated response-capable service and application query rather than changing the meaning of `list_observations`. Reusing the existing list service would make callers filter and rank full history themselves and could break existing consumers if its output changed.
- Rank each observation by its own ordering timestamp: `measurement_time` when present, otherwise `recording_time`. Interpret timestamps without a timezone as UTC for ordering, as decided by the product owner. Compare aware timestamps by instant, expose the selected timestamp normalized to UTC, and include a `time_basis` value in the projection. Preserve the original timestamps in their existing serialized fields; normalization is only for the added ordering metadata.
- Group by parameter and return every record tied at that parameter's maximum ordering timestamp. Use a stable observation identifier as a deterministic secondary response ordering only; never use it to discard tied records.
- Reuse the existing Tank and optional parameter filters. An empty match set produces an empty result. Retain the established observation serialization shape and add the ordering metadata, rather than creating a second representation of observation fields.
- Do not filter “valid” observations or select a preferred source: neither concept exists in the current data model or approved architecture. Any future validity or source preference policy requires an explicit product decision and model/spec change.

## Risks / Trade-offs

- [Records with measurement times and records without them use timestamps with different meanings] → Expose `time_basis` for every result so consumers can see whether the value represents measurement or recording time; do not imply both are equivalent evidence.
- [Timezone-naive timestamps may have originated in an unknown local zone] → Apply the product owner's explicit UTC rule for ordering and retain the original timestamp unchanged so its source representation is not lost.
- [Multiple tied records may surprise callers expecting one value] → Preserve all tied records and their provenance rather than silently choosing one.
- [The response may include a sizable number of records when many parameters have ties] → Result cardinality is bounded by the latest ties per parameter, while full history remains on the existing list service.

## Migration Plan

No data migration is required. Register the additional service alongside existing services. Rollback consists of removing the new service and query; stored observations remain unchanged.

## Open Questions

None.
