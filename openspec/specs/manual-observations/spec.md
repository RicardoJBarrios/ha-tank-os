# Manual Observations Specification

## Purpose

Provides durable manual aquarium observations that retain their original value, context, timing, method, and provenance instead of replacing history with a single current value.

## Requirements

### Requirement: Record a standalone manual observation

The system SHALL allow an authorized user to record a manual Observation for a Tank with a parameter, reported value, reported unit when known, and available measurement and recording context. The observation MAY reference a Domain Location, Sample, Method, or Instrument when applicable.

#### Scenario: Record a valid standalone observation

- **WHEN** an authorized user submits a valid parameter and reported value for a Tank
- **THEN** the system stores one manual Observation with a stable identity and the submitted context

#### Scenario: Preserve a missing measurement time

- **WHEN** the user does not know the measurement time but records the observation
- **THEN** the system stores the known recording time and leaves the measurement time unknown rather than inventing one

#### Scenario: Reject an observation without interpretable context

- **WHEN** a user submits an observation without a Tank, parameter, or interpretable reported value/state
- **THEN** the system rejects the record and explains the missing required context

### Requirement: Preserve observation provenance and qualifiers

The system MUST preserve the submitted source, method, instrument, unit, precision, and qualifiers when available. It MUST keep manual provenance distinct from future automated-source provenance.

#### Scenario: Preserve a qualified result

- **WHEN** a user records a result with a qualifier such as less-than, greater-than, or not-detected
- **THEN** the stored Observation retains the qualifier and does not convert it into an unqualified numeric value

#### Scenario: Preserve method and instrument context

- **WHEN** the user records the method or instrument used for a result
- **THEN** the Observation retains that attribution and presents it as context rather than as the source identity

### Requirement: Group partial measurement sessions

The system SHALL allow multiple manual Observations from one measurement session or Sample to be grouped together without requiring a complete fixed parameter panel. A session MAY remain partial.

#### Scenario: Save a partial session

- **WHEN** a user records only some of the parameters available for a test session
- **THEN** the system stores the submitted Observations as a partial session and does not create missing results

#### Scenario: Share sample context

- **WHEN** multiple Observations refer to the same collected Sample
- **THEN** the system allows them to share that Sample context while retaining each Observation as a separate record

### Requirement: Preserve chronological history

The system SHALL retain each accepted Observation as a separate canonical record and SHALL allow users to retrieve observations in Tank context with their available timestamps and provenance.

#### Scenario: Add a newer observation

- **WHEN** a user records a new value for a parameter already observed for the Tank
- **THEN** the system stores the new Observation without overwriting the earlier record

#### Scenario: Retrieve conflicting values

- **WHEN** valid observations for the same parameter disagree
- **THEN** the system presents the observations with their source and context and does not silently select one as the canonical replacement for the others

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

### Requirement: Correct or remove a manual observation safely

The system SHALL allow an authorized user to correct or remove a manual Observation directly, subject to dependency safeguards. A failed correction or removal MUST leave the prior canonical record unchanged.

#### Scenario: Correct an observation

- **WHEN** an authorized user submits a valid correction
- **THEN** the system updates the targeted Observation while preserving its stable identity and remaining provenance

#### Scenario: Remove an unreferenced observation

- **WHEN** an authorized user removes an Observation with no unresolved dependent record
- **THEN** the system removes it from active canonical retrieval and does not alter unrelated observations

#### Scenario: Protect a referenced observation

- **WHEN** an authorized user attempts to remove an Observation required by an active dependent record
- **THEN** the system blocks the removal or requires an explicit dependency-safe resolution and MUST NOT silently cascade-delete dependent records
