# Spec Delta

## Purpose

Lets users explicitly connect selected Home Assistant entities to aquarium context while keeping continuous entity history in Home Assistant. This avoids duplicating every state update in TankOS canonical records.

## ADDED Requirements

### Requirement: Configure explicit Home Assistant source associations

The system SHALL let an authorized user associate a selected Home Assistant entity with one existing Tank or Domain Location. Each association MUST retain the selected entity reference and the stable identity and type of its aquarium target. The system MUST NOT treat an entity name or `entity_id` as the canonical identity of a Tank or Domain Location.

#### Scenario: Associate an entity with a Tank

- **WHEN** an authorized user selects an available Home Assistant entity and an existing Tank
- **THEN** the system stores an association between that source entity and the Tank's stable identity

#### Scenario: Associate an entity with a Domain Location

- **WHEN** an authorized user selects an available Home Assistant entity and a Domain Location
- **THEN** the system stores an association with that Domain Location's stable identity and preserves its Tank context

#### Scenario: Update or remove an association

- **WHEN** an authorized user changes or removes a saved source association
- **THEN** only that association changes and canonical Tank, Domain Location, and Observation records remain unchanged

#### Scenario: Entity reference no longer resolves

- **WHEN** a saved Home Assistant entity reference is no longer available under its saved identity
- **THEN** the system presents the association as unresolved and does not silently attach a different entity

#### Scenario: Aquarium target no longer resolves

- **WHEN** a saved Tank or Domain Location target no longer exists
- **THEN** the system presents the association as unresolved and does not reassign it or change other canonical records

### Requirement: Reuse native Home Assistant entity history

The system SHALL leave continuous state history with Home Assistant Recorder and History. It MUST NOT copy every state update from an associated entity into canonical TankOS Observations or change the user's Recorder retention or inclusion settings.

#### Scenario: Review retained entity history

- **WHEN** a user reviews an associated entity that has history retained by Home Assistant
- **THEN** the user can review that source history using Home Assistant's native history capability with its source entity identity intact

#### Scenario: History is unavailable or purged

- **WHEN** Home Assistant has not retained or has purged history for an associated entity
- **THEN** TankOS creates no substitute canonical Observations and does not imply that missing history is available
