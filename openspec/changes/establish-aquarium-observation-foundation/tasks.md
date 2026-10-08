# Tasks

## 1. Validate the implementation boundary

- [x] 1.1 Run a bounded Home Assistant storage and lifecycle spike against the supported target environment, select a concrete repository adapter that satisfies atomic writes and versioned migrations, and record the environment, evidence, limits, and decision in the change documentation
- [x] 1.2 Confirm the native Home Assistant configuration and command/service surfaces for creating and retrieving the first records, and verify that the selected surface does not require a custom frontend for the approved journey
- [x] 1.3 Add or update the implementation-level contract tests for repository atomicity, migration failure behavior, and stable product identity before domain implementation proceeds

## 2. Establish domain and repository foundations

- [x] 2.1 Create the cohesive module boundaries for domain records, application commands/queries, repository ports, and Home Assistant adapters, and verify dependency direction with the repository's static or architecture checks
- [x] 2.2 Implement Tank and Domain Location value rules and stable identities, and verify creation, retrieval, duplicate-name distinction, authorization rejection, and Home Assistant identity independence with automated tests
- [x] 2.3 Implement canonical repository initialization and versioned migration handling for Tank and Domain Location records, and verify an initialized store and a failed migration preserve the defined safety behavior
- [x] 2.4 Add the native Home Assistant configuration/command adapter for Tank and Domain Location mutations and retrieval, and verify it routes every write through the application boundary without direct persistence access
- [x] 2.5 Document the supported first-run setup and the observable Tank/Domain Location workflow in the repository's English technical documentation, and verify every command and path in the documentation exists

## 3. Implement manual observation capture

- [x] 3.1 Define the Observation, provenance, timestamp, qualifier, and partial-session domain rules from the `manual-observations` specification, and verify required-field and unknown-time behavior with automated tests
- [x] 3.2 Implement creation of standalone and grouped partial manual observations, and verify that shared Sample context and optional Method/Instrument context remain attributable without requiring a complete panel
- [x] 3.3 Implement chronological observation retrieval in Tank context, and verify that newer or conflicting values do not overwrite or silently replace earlier observations
- [x] 3.4 Implement direct correction and dependency-safe removal, and verify failed mutations are atomic and do not cascade-delete dependent records
- [x] 3.5 Add the native Home Assistant capture and retrieval adapter, and verify manual provenance, reported units, precision, qualifiers, and available timestamps survive the adapter boundary unchanged
- [x] 3.6 Document the first manual observation workflow and its provenance limitations, and verify the workflow identifies what is manual, what is unknown, and what remains outside this change

## 4. Integrated verification and handoff

- [x] 4.1 Run the relevant unit, integration, Home Assistant compatibility, lint, type, and structural OpenSpec checks, and retain the exact commands, versions, results, and relevant limits
- [x] 4.2 Exercise the end-to-end journey of creating a Tank, adding a Domain Location, recording a partial manual session, retrieving its history, correcting one observation, and protecting a referenced record from removal
- [x] 4.3 Review the implementation against the proposal, both capability specs, the architecture spine, and the product baseline, and record any discrepancy as an owning-source correction before requesting product-owner validation
