# Design

## Context

Trace references already represent locators. This change adds a portable, content-addressed manifest that can be attached to a run or handoff.

## Goals / Non-Goals

**Goals:** stable manifests, SHA-256 verification, source references, and explicit derived status.

**Non-Goals:** artifact storage, publication, canonical-document promotion, or remote signing.

## Decisions

Use a JSON-serializable dataclass and stream files in chunks when hashing. Missing and changed states are explicit. Source references are metadata only and are not recursively embedded.

## Risks / Trade-offs

- [Risk] A digest proves bytes, not semantic correctness. → Mitigation: retain evaluation and product-owner validation separately.
- [Risk] Locators can become invalid after moves. → Mitigation: preserve missing state and source provenance rather than silently updating it.

## Migration Plan

Create manifests for new evidence-producing flows; existing artifacts remain unregistered until explicitly adopted.

## Open Questions

None.
