# Design

## Context

See [proposal.md](./proposal.md) for the motivation and bounded product scope. The product baseline establishes a native Home Assistant integration with a modular hexagonal core, ha-tank-os-owned canonical persistence, explicit provenance, and application commands and queries as the core boundary.

The repository has no existing OpenSpec capability specifications or product implementation. The design therefore defines the first durable seams without selecting an unverified storage library, Home Assistant version, or custom frontend framework.

## Goals / Non-Goals

**Goals:**

- Establish domain-level Tank, Domain Location, Observation, and partial-session boundaries.
- Keep canonical records independent from Home Assistant entity identity and Recorder retention.
- Provide one write path and query path that later Home Assistant adapters can reuse.
- Make provenance, timestamps, qualifiers, correction, and dependency-safe removal explicit.
- Keep the first implementation small enough to validate the product's recording workflow.

**Non-Goals:**

- Automatic Home Assistant entity ingestion or association suggestions.
- Prepared-water, transfers, top-offs, operations, calculators, trend views, prediction, or physical actuation.
- A public REST API, external service, cloud analytics, or required plugin.
- One Home Assistant entity per historical record.
- A final choice of concrete persistence API or runtime version before that choice is verified against the supported Home Assistant environment.

## Decisions

### Domain core owns canonical meaning

The implementation SHALL place Tank, Domain Location, Observation, and session invariants behind a domain/application boundary. Home Assistant configuration, services, entities, and any future UI act as adapters and MUST NOT write directly to persistence.

**Alternative considered:** put the records directly in Home Assistant entities or helpers. Rejected because entity identity, Recorder retention, and presentation state do not provide the required canonical provenance and relationship semantics.

### Stable product identities are separate from Home Assistant identities

Each canonical record receives a product identity. Home Assistant entity IDs, labels, and registry entries may be stored as integration context later, but they are not authoritative identifiers.

**Alternative considered:** use entity IDs as foreign keys. Rejected because entity IDs and labels can change independently of aquarium meaning.

### Repository boundary with explicit transactional operations

The application layer SHALL use a repository port for canonical reads and writes. The concrete persistence adapter SHALL provide atomic record mutations and versioned migration handling. Selecting the concrete Home Assistant storage mechanism is a prerequisite technical validation for implementation, not a product behavior decision.

**Alternative considered:** use Recorder as the primary archive. Rejected because Recorder retention, purge, aggregation, and entity-centric semantics do not guarantee the required manual-record history and provenance.

### Observations are append-oriented facts with controlled correction

New observations create new records. Corrections target one stable record, and removal is blocked when active dependencies would become invalid. A failed mutation MUST be atomic from the caller's perspective.

**Alternative considered:** maintain only the latest value per parameter. Rejected because the product explicitly needs chronological comparison and disagreement visibility.

### Native Home Assistant surfaces first

The initial adapter should use native Home Assistant configuration and service/command surfaces where they can express the approved workflow. A custom frontend is not required for this change; any remaining usability gap must be demonstrated before custom UI is added.

**Alternative considered:** build a custom dashboard first. Rejected because it would duplicate native capabilities before their fit is verified.

### Manual source is explicit and future-source compatible

Manual capture records a manual source classification and preserves optional method, instrument, and sample context. The source model remains extensible so a later Home Assistant adapter can add automated provenance without changing the meaning of manual records.

**Alternative considered:** model manual and automated data as unrelated record types. Rejected because the product requires coherent querying while preserving source differences.

## Risks / Trade-offs

- [Risk] The concrete Home Assistant persistence mechanism may not satisfy all transactional and migration requirements. → Mitigation: run a bounded technical validation before implementation and keep the repository port independent of the adapter.
- [Risk] A first native Home Assistant surface may be less convenient than a custom UI. → Mitigation: validate the core capture journey with the native surface and record any material gap before proposing custom UI.
- [Risk] Dependency-safe removal may initially reject some apparently simple corrections. → Mitigation: expose the blocking dependency clearly and keep cascade behavior explicit rather than silent.
- [Risk] Optional sample, method, and instrument references could expand the first change. → Mitigation: require only the observation's interpretable context in this change; full lifecycle management of those reference records remains a later bounded change unless implementation validation proves it necessary.

## Migration Plan

There is no existing product data or implementation to migrate. The implementation must provide versioned initialization for the new canonical repository and must fail safely if initialization or migration cannot preserve the defined record semantics. Rollback before any production data exists is a deployment rollback; after data exists, rollback must preserve or export canonical records before downgrading.

## Open Questions

- Which supported Home Assistant versions and concrete storage adapter satisfy the repository contract will be resolved by a bounded technical validation before implementation.
- The exact native configuration/service interaction shape will be selected during implementation design after confirming current Home Assistant APIs; it must not change the observable requirements in the specs.
