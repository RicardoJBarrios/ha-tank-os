# Spec Delta

## Purpose

Lets each Tank configure its own measurement parameters and lifecycle profiles while using editable aquarium-type starters without imposing universal water-quality targets.

## ADDED Requirements

### Requirement: Configure Tank parameters from editable starters

The system SHALL provide freshwater and marine starter templates that an owner can apply to a Tank and customize for that Tank without changing another Tank's configuration. The system SHALL allow owners to add custom parameters and SHALL NOT restrict observations to a closed product-wide catalog. Each parameter SHALL have a stable identity and distinguish its measured quantity from its display label so that different quantities, including nitrate and nitrate-nitrogen, are not conflated. Applying or editing a template SHALL NOT rewrite existing observations.

#### Scenario: Apply and customize a starter template

- **WHEN** an owner applies a freshwater or marine starter template to a Tank and changes one of its parameters
- **THEN** the Tank receives an editable configuration and the change does not alter another Tank's configuration unless the owner explicitly applies it there

#### Scenario: Add a custom parameter

- **WHEN** an owner adds a parameter that is not in a starter template
- **THEN** the parameter receives its own stable identity and can be used for later observations

#### Scenario: Keep distinct quantities separate

- **WHEN** parameters such as nitrate and nitrate-nitrogen are configured
- **THEN** the system represents them as distinct quantities and does not silently reinterpret one as the other

#### Scenario: Preserve configuration history

- **WHEN** an owner edits or removes a configured parameter from future use
- **THEN** earlier observations remain retrievable with the definition and unit context that applied when each observation was recorded

### Requirement: Manage lifecycle phases and measurement profiles

The system SHALL provide initial lifecycle phases for cycling, maturation, and established operation, and SHALL allow the owner to add and modify phases and their associated measurement profiles. The owner SHALL be able to identify and change a Tank's current phase. The active profile SHALL guide which configured parameters are relevant for future capture. Profiles SHALL NOT imply universal target values or measurement frequencies.

#### Scenario: Use the current phase profile for future capture

- **WHEN** an owner requests measurement guidance for a Tank
- **THEN** the system presents parameters from that Tank's current lifecycle-phase profile

#### Scenario: Do not infer an unselected lifecycle phase

- **WHEN** no lifecycle phase has been explicitly selected for a Tank
- **THEN** the system does not assign a phase from Tank age or another assumption and reports that no phase profile is selected

#### Scenario: Change a Tank's current phase

- **WHEN** an owner changes a Tank's current lifecycle phase
- **THEN** future capture guidance uses the newly selected phase's profile and prior observations retain their recorded phase context

#### Scenario: Add or modify a lifecycle phase

- **WHEN** an owner creates or edits a phase and its measurement profile
- **THEN** the change is available to that Tank's future capture guidance without reclassifying historical observations

#### Scenario: Do not present universal targets

- **WHEN** a profile is used to guide measurement capture
- **THEN** the system does not imply that a parameter target or testing frequency is universal or was configured unless one is explicitly recorded
