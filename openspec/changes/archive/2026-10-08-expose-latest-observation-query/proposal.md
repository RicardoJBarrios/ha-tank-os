# Proposal

## Why

TankOS can record and list manual observations, but callers cannot request the latest chronological observation for each parameter through a focused response. A native Home Assistant query will make current evidence usable in scripts and dashboards while preserving its source and context.

## What Changes

- Add a response-capable native service query for the latest observation per parameter, with an optional parameter filter.
- Preserve observation history and the existing full-list query; return provenance and time-basis details so callers can interpret the result.
- Do not add entities, a custom dashboard, Recorder mirroring, telemetry ingestion, or an observation-validity model.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `manual-observations`: Define a native query that returns the latest chronological observation or tied observations per parameter, retaining source and context.

## Impact

The existing `manual-observations` behavior and native service surface are extended. Expected implementation areas are the application query and Home Assistant service registration, with focused unit and integration coverage. Persistence format and existing observation records remain unchanged.
