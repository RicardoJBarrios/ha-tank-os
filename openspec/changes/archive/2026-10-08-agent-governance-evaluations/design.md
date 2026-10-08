# Design

## Context

The generic evaluation harness accepts structured results. This change adds a named governance checklist on top of that primitive.

## Goals / Non-Goals

**Goals:** eleven independent checks, fail-closed handling of missing evidence, provenance keys, and stable JSON output.

**Non-Goals:** discovering evidence implicitly, changing Git branches, running tools, approving product scope, or replacing human review.

## Decisions

Represent evidence as a mapping of stable keys to booleans or structured details supplied by the caller. The evaluator only interprets explicit truth values; adapters remain responsible for collecting evidence from context packs, traces, CI, Git, and handoff records. The checklist intentionally contains eleven entries because the requested list contains eleven distinct controls.

## Risks / Trade-offs

- [Risk] A caller could provide inaccurate evidence. → Mitigation: retain evidence keys/details, link reports to trace runs, and require independent collection adapters.
- [Risk] Automated checks cannot assess every semantic decision. → Mitigation: keep product-owner validation pending and document limitations.

## Migration Plan

Add the checklist and run it in local/CI evaluation jobs once evidence adapters are available.

## Open Questions

None.
