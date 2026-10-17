# Spec Delta

## MODIFIED Requirements

### Requirement: Record a standalone manual observation

The system SHALL allow an authorized user to record a manual Observation for a Tank with a parameter, reported value, reported unit when known, and available measurement and recording context. The observation MAY reference a Domain Location, Sample, Method, or Instrument when applicable. When a configured parameter and current lifecycle phase apply, the Observation SHALL retain an immutable snapshot of the parameter definition and phase context used at capture, including the parameter's stable identity, measured-quantity identity, display label and configured unit, and the phase identity and display name. The system SHALL NOT infer these contexts for observations recorded before the configuration exists.

#### Scenario: Record a valid standalone observation

- **WHEN** an authorized user submits a valid parameter and reported value for a Tank
- **THEN** the system stores one manual Observation with a stable identity and the submitted context

#### Scenario: Preserve a missing measurement time

- **WHEN** the user does not know the measurement time but records the observation
- **THEN** the system stores the known recording time and leaves the measurement time unknown rather than inventing one

#### Scenario: Reject an observation without interpretable context

- **WHEN** a user submits an observation without a Tank, parameter, or interpretable reported value/state
- **THEN** the system rejects the record and explains the missing required context

#### Scenario: Snapshot configured parameter and phase context

- **WHEN** an Observation is recorded while a configured parameter and current lifecycle phase apply
- **THEN** the Observation retains the definition and phase details as they existed at capture, even if the owner later changes or removes that configuration

#### Scenario: Leave historical context unknown when it was not recorded

- **WHEN** an Observation predates parameter and lifecycle configuration or has no such context
- **THEN** the system preserves it without assigning a guessed parameter definition or lifecycle phase
