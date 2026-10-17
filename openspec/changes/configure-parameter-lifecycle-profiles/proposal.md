# Proposal

## Why

TankOS currently accepts parameter names as free text and has no Tank-specific lifecycle profile to guide future observations. Configurable parameter definitions, editable freshwater and marine starters, and lifecycle profiles will make capture consistent while preserving the meaning and context of earlier records.

## What Changes

- Add Tank-scoped parameter configuration and editable freshwater and marine starter templates; custom parameters remain supported.
- Add editable lifecycle phases and parameter profiles, with cycling, maturation, and established operation as initial phases.
- Capture the parameter-definition and lifecycle context that applied when an Observation was recorded, so later configuration edits do not reinterpret history.
- Keep profile values as capture guidance. Do not add universal target ranges, test cadence, a custom dashboard, or a fixed parameter catalog.

## Capabilities

### New Capabilities

- `parameter-lifecycle-profiles`: Configure Tank-specific parameters, starter templates, lifecycle phases, and the profile used for future capture.

### Modified Capabilities

- `manual-observations`: Preserve the applicable parameter definition and lifecycle context with each newly recorded Observation.

## Impact

Expected areas include domain and canonical persistence models, application commands and queries, Home Assistant-native configuration services, observation serialization, migration handling for existing records, and focused integration tests. Existing observations must remain readable without an inferred historical phase or parameter definition.
