# Proposal

## Why

ha-tank-os needs a small, durable product foundation before it can connect Home Assistant sources or support aquarium operations. Without stable aquarium context and attributable manual observations, later features would have no trustworthy ownership, provenance, or history boundary.

This is the first bounded product change because the approved capability sequence starts with domain identity and manual observation capture (`CAP-01` and `CAP-02`). It validates the core value without committing the product to high-volume telemetry ingestion, custom dashboards, or physical control.

## What Changes

- Introduce stable aquarium and domain-location records that are independent of Home Assistant entity names.
- Allow the owner to create and retrieve multiple Tanks and their relevant Domain Locations.
- Introduce manual Observation records linked to a Tank and optionally to a Domain Location, Sample, Method, and Instrument.
- Preserve reported values, units, precision, qualifiers, provenance, and distinct available timestamps without overwriting earlier observations.
- Support standalone observations and grouped partial measurement sessions.
- Allow observations to be corrected or removed subject to dependency-safe behavior defined by the product contract.
- Establish the application write boundary and canonical persistence boundary for these records.
- Keep Home Assistant source ingestion, automatic association, prepared-water tracking, operations, custom dashboards, predictions, and physical actuation outside this change.

## Capabilities

### New Capabilities

- `aquarium-context`: Stable Tanks and Domain Locations with owner-visible identity and retrieval behavior.
- `manual-observations`: Attributable manual observations and partial measurement sessions linked to aquarium context.

### Modified Capabilities

None. The repository has no existing OpenSpec capability specifications.

## Impact

- Establishes the first product-facing domain contracts for the future native Home Assistant integration.
- Defines the minimum application, persistence, and provenance boundaries that later changes must reuse.
- Does not require an external service, public API, Home Assistant source association, Recorder mirroring, plugin dependency, or custom frontend.
- Requires product and domain tests for identity, provenance, timestamps, correction, deletion safeguards, and partial sessions when implementation begins.
