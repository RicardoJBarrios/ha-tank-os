# Proposal

## Why

As the repository grows, agents will need to work across requirements,
architecture, ADRs, OpenSpec changes, source code, tests, and Home Assistant
integration material without loading the entire repository or confusing stale
documents with current authority. The project needs a reproducible context
selection mechanism now so future semantic retrieval can extend it without
becoming the source of truth.

## What Changes

- Add an authority-aware context model for repository artifacts and explicit
  relationships between changes, specifications, decisions, source, and tests.
- Add a deterministic context resolver that builds a bounded context pack from
  an active OpenSpec change and its declared dependencies.
- Add freshness tracking, content-addressed cache keys, and incremental
  invalidation so unchanged context is reused and changed context is
  recalculated transparently.
- Add local lexical discovery as a fallback for relevant symbols, paths, and
  terms, while preserving authority and freshness rules.
- Store the derived index in a disposable or regenerable local SQLite database
  or equivalent local file, without making it a canonical project database.
- Define an extension point for later semantic retrieval and graph traversal,
  without requiring a vector database, hosted service, or full GraphRAG stack
  in this change.
- Document commands, metadata, authority precedence, invalidation, privacy,
  refresh points, cache reuse, and reproducibility requirements for context
  packs.

## Capabilities

### New Capabilities

- `context-resolver`: Authority-aware deterministic context packs and local
  discovery for agents working on bounded changes.

### Modified Capabilities

None.

## Impact

- Adds repository tooling, metadata/schema files, generated local index state,
  context-pack output, and tests.
- Adds no runtime Home Assistant dependency and no external database service.
- May add a lightweight Python or Node dependency only if the selected design
  cannot use the existing repository toolchain.
- Requires updates to agent instructions and operational tooling documentation.
- Does not change product domain behavior, Home Assistant persistence, or the
  authority of requirements, architecture, ADRs, or OpenSpec artifacts.
