# Design

## Context

The trace store is local operational data. Canonical documentation, repository history, product persistence, and Home Assistant Recorder are not retention targets.

## Goals / Non-Goals

**Goals:** explicit classification, dry-run-first behavior, bounded deletion, idempotency, and privacy-safe reports.

**Non-Goals:** legal policy automation, remote backups, product data lifecycle, or undelete guarantees.

## Decisions

Use a typed retention policy with target `operational_trace` only in this increment. Purge previews query eligible runs before any write. Confirmed purge deletes child events/references and then runs in a transaction, returning counts. The default API is dry-run and requires `confirm=True` for deletion.

## Risks / Trade-offs

- [Risk] Purged traces cannot be recovered from the local store. → Mitigation: dry-run default, explicit confirmation, export before purge, and clear report.
- [Risk] Retention metadata may be sensitive. → Mitigation: reports contain counts and timestamps only.

## Migration Plan

Adopt a documented default retention window only after the product owner chooses it. Until then, no automatic purge is scheduled.

## Open Questions

None.
