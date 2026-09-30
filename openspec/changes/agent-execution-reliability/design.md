# Design

## Context

This is a pure policy layer used by future tool adapters. It complements traceability, observability, and permissions without performing external effects.

## Goals / Non-Goals

**Goals:** deterministic decisions, bounded exponential backoff, idempotency gating, deadlines, and cancellation.

**Non-Goals:** a job queue, distributed locking, provider-specific exception hierarchies, or automatic operation execution.

## Decisions

Use immutable policy configuration and an explicit `Decision` result. Failure classification is supplied by the adapter using a small enum. Backoff is capped and deterministic from attempt number; jitter is intentionally excluded from the policy result so callers can add it without compromising testability.

## Risks / Trade-offs

- [Risk] An adapter may misclassify a non-idempotent operation. → Mitigation: require `idempotent=True` for every retry decision.
- [Risk] Long-running work may outlive its caller. → Mitigation: require an absolute deadline and explicit cancellation state.

## Migration Plan

Add the policy module and use it from agent/tool adapters before adding asynchronous workers.

## Open Questions

None.
