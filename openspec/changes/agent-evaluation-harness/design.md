# Design

## Context

The harness consumes structured execution results and can attach an evidence reference to the existing trace. It does not invoke providers or tools itself.

## Goals / Non-Goals

**Goals:** versioned cases, deterministic checks, bounded evidence, and explicit human-validation state.

**Non-Goals:** model benchmarking claims, external evaluation services, transcript storage, or automatic product acceptance.

## Decisions

Use a small immutable case dataclass and a pure evaluator. Required/forbidden markers operate on a caller-provided bounded text summary. Latency is checked against an optional threshold. Results use stable JSON keys and can be attached to a trace as an artifact reference.

## Risks / Trade-offs

- [Risk] Marker checks can miss semantic errors. → Mitigation: treat them as regression gates, not proof of product correctness.
- [Risk] Large outputs may leak secrets. → Mitigation: cap and redact the supplied summary before evidence generation.

## Migration Plan

Add cases incrementally and run them in CI or local development; require product-owner validation for acceptance.

## Open Questions

None.
