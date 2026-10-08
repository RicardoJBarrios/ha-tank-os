# Aquarium Context Specification

## Purpose

Provides stable aquarium and domain-location context so every future aquarium record can be associated with the correct managed system without depending on Home Assistant entity names.

## Requirements

### Requirement: Manage multiple tanks

The system SHALL allow an authorized Home Assistant user to create, view, update, and remove multiple Tank records. Each Tank MUST have a stable product identity independent of its display name and any Home Assistant entity identifier.

#### Scenario: Create a tank

- **WHEN** an authorized user submits a valid tank name
- **THEN** the system creates one Tank with a stable identity and returns the created Tank context

#### Scenario: Distinguish tanks with similar names

- **WHEN** two Tanks have the same or similar display names
- **THEN** the system keeps them distinguishable by their stable identities and context

#### Scenario: Reject an unauthorized tank mutation

- **WHEN** a user without permission attempts to create, update, or remove a Tank
- **THEN** the system rejects the mutation and does not change canonical records

### Requirement: Manage domain locations

The system SHALL allow an authorized user to create, view, update, and remove Domain Locations associated with a Tank. A Domain Location MUST remain distinct from a user's geographic or Home Assistant installation location.

#### Scenario: Associate a domain location with a tank

- **WHEN** an authorized user creates a Domain Location for a Tank
- **THEN** the system stores the location with its own stable identity and returns its Tank association

#### Scenario: Retrieve a tank context

- **WHEN** a user requests a Tank context
- **THEN** the system returns the Tank and its active Domain Locations with stable identities

#### Scenario: Prevent removal of a referenced location

- **WHEN** a user attempts to remove a Domain Location referenced by an active canonical record
- **THEN** the system rejects the removal or requires an explicit dependency-safe resolution, and MUST NOT silently reassign or cascade-delete the referenced record

### Requirement: Preserve product identity across Home Assistant changes

The system MUST NOT use a Home Assistant `entity_id`, display label, or registry name as the canonical identity of a Tank or Domain Location.

#### Scenario: Home Assistant label changes

- **WHEN** a related Home Assistant label or entity identifier changes
- **THEN** the Tank and Domain Location identities and their canonical associations remain unchanged
