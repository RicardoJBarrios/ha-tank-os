# Proposal

## Why

TankOS currently records manual aquarium observations but cannot associate an existing Home Assistant entity with a Tank or Domain Location. Home Assistant already maintains entity history through its native Recorder and History features, so the first source-association slice can make that history usable without copying every entity update into permanent TankOS records.

## What Changes

- Let an authorized user explicitly associate selected Home Assistant entities with existing Tanks or Domain Locations.
- Preserve Home Assistant as the source of continuous entity history; TankOS will not import every entity update into canonical observations in this change.
- Keep missing or renamed entity references visible as unresolved associations; never silently attach a different entity.
- Leave automatic association suggestions, equipment targets, and any future selective canonical telemetry ingestion for later bounded changes.

## Capabilities

### New Capabilities

- `ha-source-associations`: Explicitly associate selected Home Assistant entities with aquarium context and reuse native Home Assistant history.

### Modified Capabilities

None.

## Impact

- Extends the Home Assistant config-entry options flow and association configuration.
- Reads existing Tank and Domain Location identities from the canonical repository when offering targets.
- Uses Home Assistant entity registry and native History/Recorder behavior; adds no dependency and does not change Recorder retention settings.
- Does not change manual observation storage, import telemetry, add actuator controls, or implement suggestion generation.
