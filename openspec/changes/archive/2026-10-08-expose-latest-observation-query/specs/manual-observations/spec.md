# Spec Delta

## ADDED Requirements

### Requirement: Query the latest observation for each parameter
The system SHALL provide a native query that returns the latest recorded observation for each parameter in a Tank, optionally restricted to one parameter. The query SHALL preserve each returned observation's value, unit, qualifier, source, provenance, context, identity, and timestamps. It SHALL identify whether the ordering timestamp is the measurement time or, when that is absent, the recording time. A timestamp without a timezone SHALL be interpreted as UTC for ordering, while its stored and returned original value remains unchanged. The query SHALL NOT infer validity or silently prefer a source or method because the observation model has no validity status.

#### Scenario: Return the latest observation per parameter
- **WHEN** a caller queries the latest observations for a Tank with observations for multiple parameters
- **THEN** the response contains the latest observation for each parameter, ordered by measurement time when present and otherwise by recording time, interprets timestamps without a timezone as UTC, and identifies the time basis for each result

#### Scenario: Restrict the query to one parameter
- **WHEN** a caller supplies a parameter filter
- **THEN** the response contains only the latest observation or tied latest observations for that parameter

#### Scenario: Preserve tied latest observations
- **WHEN** multiple observations for the same parameter share the latest ordering timestamp
- **THEN** the response includes all tied observations with their separate sources and contexts

#### Scenario: No observations match
- **WHEN** a Tank has no observations, or none match the optional parameter filter
- **THEN** the response returns an empty result without fabricating an observation

#### Scenario: Do not claim validity
- **WHEN** the query returns observations
- **THEN** the response does not label them valid or discard them based on an unmodeled validity status
