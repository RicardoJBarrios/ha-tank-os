# Design

## Context

The trace store already provides ordered, redacted events. This change adds authorization before tool execution and uses the trace only for decision evidence.

## Goals / Non-Goals

**Goals:** deterministic matching, deny-by-default, scoped approvals, expiry, single-use consumption, and trace integration.

**Non-Goals:** identity management, remote approval UI, operating-system sandboxing, or changing the local Home Assistant MCP configuration.

## Decisions

Use an immutable in-memory policy object loaded from explicit configuration. Rules match exact operation names and glob-like resource scopes, with deny taking precedence over allow and approval rules. Approval records are short-lived in-memory objects identified by opaque IDs; the ID itself is never written to trace payloads. The policy evaluator is synchronous and side-effect free unless a trace store is explicitly provided.

## Risks / Trade-offs

- [Risk] A permissive rule can grant broad access. → Mitigation: require explicit policy files and expose the matched rule in every decision.
- [Risk] In-memory approvals disappear on restart. → Mitigation: fail closed and require a new approval.
- [Risk] Policy decisions can be recorded but execution can still be bypassed by an unintegrated caller. → Mitigation: document the evaluator as the mandatory adapter boundary and add integration tests for the supported CLI/tool path.

## Migration Plan

Add the evaluator and tests first. Integrate it at agent tool adapters without changing product state. Existing broad local access must be represented by a deliberate allow rule.

## Open Questions

None.
