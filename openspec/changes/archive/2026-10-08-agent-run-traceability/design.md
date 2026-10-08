# Design

## Context

See [proposal.md](./proposal.md) for the motivation and scope. The repository already has a context resolver that produces derived context packs with cache keys and source hashes. The trace must be a separate agent-platform operational store: it must not become a product database, an authoritative Home Assistant Recorder, or an external telemetry dependency.

## Goals / Non-Goals

**Goals:**

- Provide a deterministic local record for run lifecycle, ordered events, provenance, and evidence references.
- Make event history tamper-evident and verifiable without requiring a remote service.
- Make redaction mandatory at the persistence and export boundary.
- Support interrupted local development runs and explicit recovery.
- Keep the interface provider-neutral so BMAD, Spec Kit, OpenSpec, VS Code agents, and future providers can use it.

**Non-Goals:**

- Enforce permissions or approval policy; that is a subsequent change.
- Provide dashboards, distributed telemetry, alerting, cost accounting, or model routing.
- Store product entities, Home Assistant state, full source files, secrets, or complete tool transcripts by default.
- Replace Git history, OpenSpec artifacts, context-pack manifests, or human product-owner validation.

## Decisions

### Local SQLite operational store with portable export

Use a local SQLite database for indexed run/event/reference queries and a versioned redacted export format for handoff and evidence collection. SQLite is preferred over JSONL-only storage because lifecycle updates, parent-child queries, and integrity verification need transactional consistency. JSONL remains a useful export shape, not the primary mutable store.

The database lives under an ignored agent-platform state directory. The location is configurable so tests can use temporary files and future deployments can select a managed volume.

### Append-only events with canonical hash chaining

Run metadata may transition through the defined lifecycle, but event rows are append-only. Each event stores a canonical serialized representation, its predecessor integrity value, and a cryptographic digest over the canonical content plus predecessor. A per-run sequence and database uniqueness constraints prevent ambiguous ordering. Verification recomputes the chain rather than trusting stored status.

### Explicit schemas and references instead of copied content

Run, event, tool-call, and artifact-reference records use versioned schemas with stable identifiers. Large or sensitive content is referenced by locator and digest where appropriate; it is not copied into the trace unless a later policy explicitly permits it. Missing references remain visible as unresolved rather than being silently discarded.

### Redaction before persistence

Redaction is performed before event serialization and database writes, not only at presentation time. The implementation will centralize configurable patterns for tokens, credentials, authorization headers, and known secret environment variables. Redaction metadata records what class was removed, never the original value.

### Context resolver integration by immutable identity

A run records the repository revision, registry identity, resolver version, and context-pack cache key/manifest identifier when a pack is used. The trace does not duplicate pack contents; the context resolver remains authoritative for derived context and its source documents remain authoritative for requirements.

### Explicit recovery, no automatic deletion

Startup may report stale runs, but only an explicit operator or controlled command may mark one abandoned. Recovery appends a recovery event, preserves all prior events, and records the stale threshold and reason used.

### Alternatives considered

- **External observability service:** rejected for the first increment because local development must work offline and the user requested local control; an adapter can be added later.
- **Home Assistant Recorder:** rejected because it is product/runtime history and is not a provider-neutral agent execution authority.
- **Versioned files only:** rejected as the primary store because concurrent appends and parent-child queries are error-prone, though portable exports remain file-based.
- **Opaque full transcripts:** rejected because they increase privacy risk and couple the contract to providers; structured redacted events and references are sufficient for the initial trace.

## Data and interface boundaries

The implementation should expose operations equivalent to `start`, `append event`, `finish`, `inspect`, `export`, `verify`, and explicit `recover`. Each operation must return stable identifiers, schema versions, and actionable validation errors. The command/API naming is an implementation choice as long as the observable requirements remain intact.

## Risks / Trade-offs

- [Risk] A local database can be deleted or corrupted. → Mitigation: provide integrity verification, portable exports, clear retention documentation, and never treat the local trace as the only copy of canonical project decisions.
- [Risk] Redaction patterns can miss an unexpected secret format. → Mitigation: default-deny sensitive fields, test representative providers and headers, and add the later privacy control before broadening retention.
- [Risk] Hash chaining detects alteration but does not prove external authenticity. → Mitigation: describe it as tamper-evident, retain repository/export digests, and defer signing or remote notarization until there is a concrete need.
- [Risk] Agent/provider schemas evolve. → Mitigation: version the record and event envelopes, preserve unknown fields where safe, and require migration tests for schema changes.
- [Risk] Concurrent writers may contend on SQLite. → Mitigation: use transactions, bounded busy timeouts, and deterministic retry behavior; document the local concurrency limit.

## Migration Plan

1. Add the store schema, redaction, canonicalization, and integrity primitives behind tests.
2. Add the local inspection/export/verification interface and context-pack provenance adapter.
3. Integrate one agent execution path and record compatibility evidence without changing product behavior.
4. Validate recovery, concurrent append behavior, redaction, and export round trips.
5. Rollback consists of disabling the integration and preserving or removing only the ignored operational store; no product data migration is required.

## Open Questions

None for this change. Retention duration, remote export, approval policy, and dashboard/metrics semantics are intentionally separate decisions.
