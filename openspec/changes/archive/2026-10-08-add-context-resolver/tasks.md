# Tasks

## Metadata and authority model

- [x] Define the versioned `.context/registry.json` schema for artifact
  identity, kind, authority, freshness, relationships, tags, and exclusions.
- [x] Register the existing repository authorities, OpenSpec locations, agent
  instructions, and relevant tooling documentation without duplicating their
  contents.
- [x] Add validation for paths, relationship targets, status values, duplicate
  identities, authority precedence, and forbidden sensitive/runtime paths.
- [x] Define source identities, pack cache keys, freshness states, and
  dependency-aware invalidation reasons.

## Resolver and index

- [x] Implement the Python resolver CLI with `validate`, `index`, `search`, and
  `pack` commands and stable JSON output.
- [x] Implement the local SQLite metadata and FTS index with a documented
  deterministic fallback when FTS5 is unavailable.
- [x] Implement mandatory and explicit-link context traversal with authority,
  freshness, relationship-distance, and character-budget handling.
- [x] Implement cheap preflight, pack reuse, dependent invalidation, explicit
  `--rebuild`, incompatible-schema invalidation, and refresh boundaries.
- [x] Implement the provider-neutral retrieval candidate interface and keep
  optional semantic/graph providers disabled by default.
- [x] Exclude secrets, ignored runtime state, generated reports, database files,
  and Home Assistant local state from indexing and packs.
- [x] Add generated-path and database handling to repository ignore rules.

## Integration and documentation

- [x] Add package scripts for validation, indexing, searching, and context-pack
  generation, using the repository's canonical Python environment.
- [x] Document the context model, authority precedence, metadata format,
  commands, pack format, regeneration, limitations, and future retrieval
  extension in English.
- [x] Add agent guidance requiring context packs for bounded changes when the
  resolver is available and preserving direct authority reads.
- [x] Add a reproducible example pack for an active OpenSpec change without
  committing generated local database state.
- [x] Make pack manifests expose cache identity, freshness state, reused and
  recalculated entries, input hashes, and refresh reasons.

## Verification

- [x] Unit-test registry validation, authority filtering, link traversal,
  search ranking, budgets, redaction, deterministic ordering, cache reuse,
  dependency invalidation, explicit rebuilds, and refresh evidence.
- [x] Add integration tests that build and inspect a pack from fixture artifacts.
- [x] Run Python, frontend, secret, spelling, Markdown, OpenSpec, and diff
  quality gates and record exact results.
- [x] Perform an independent review of authority precedence and sensitive-path
  exclusions before marking the change complete.
