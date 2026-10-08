# Design

## Context

The repository currently has authoritative instructions and OpenSpec change
boundaries, but no machine-readable context graph or reproducible context-pack
command. The change is repository tooling; it does not alter Home Assistant
product behavior or domain persistence.

## Goals / Non-Goals

**Goals:**

- Make authority, freshness, and artifact relationships explicit.
- Build bounded context packs for active OpenSpec changes.
- Provide deterministic local discovery with no hosted service.
- Keep derived indexes disposable and reproducible.
- Leave a stable interface for future semantic and graph retrieval.

**Non-Goals:**

- Do not introduce Neo4j, Qdrant, a hosted vector service, embeddings, or a
  full GraphRAG pipeline in this change.
- Do not replace OpenSpec, BMAD, `AGENTS.md`, PRDs, architecture, ADRs, or
  product specifications as authorities.
- Do not index Home Assistant runtime state, secrets, credentials, or generated
  reports.
- Do not create a product database or persist domain data.

## Decisions

### Versioned metadata plus a derived SQLite index

Versioned metadata and relationships will be kept in a small JSON registry under
`.context/`. A local SQLite database under `.context/generated/` will contain
derived artifact metadata and a lexical FTS index. SQLite is selected over a
Docker database because the first capability is single-developer, local,
regenerable tooling with no service lifecycle or network boundary. The database
is disposable and ignored.

### A Python standard-library resolver

The resolver will use a Python command-line module and the existing `uv`
environment. Python's standard-library `sqlite3`, hashing, JSON, pathlib, and
argument parsing are sufficient for the first implementation, avoiding a new
runtime dependency. The implementation will provide stable machine-readable
JSON output and human-readable Markdown packs.

### Explicit links before discovery

The resolver will load mandatory files and traverse explicit registry links
first. It will then use local lexical search only for discovery candidates.
Authority precedence will be encoded and tested so a semantically similar
archived document cannot override an accepted current artifact.

### Stable pack ordering and budgets

Artifacts will be ordered by authority rank, relationship distance, path, and
content hash. A configurable character budget will be enforced. Mandatory
files are non-evictable; linked and discovery material is included only when it
fits, and the manifest records all exclusions.

### Incremental freshness and cache lifecycle

The resolver will compute a `SourceIdentity` for every input from its relative
path, content hash, registry metadata hash, and relevant status. The pack cache
key will include the active change and task, repository revision when available,
registry hash, resolver version, authority-policy hash, selection budget, and
reachable dependency identities.

At pack generation, a cheap preflight compares current source identities with
the cached manifest. Unchanged entries and packs are reused. A changed source
invalidates its own index entry and all dependent packs; unrelated changes do
not trigger a full rebuild. An explicit `--rebuild` or an incompatible schema
or resolver version invalidates the whole derived index.

Refresh is synchronous at explicit boundaries—pack generation, task start,
before a mutating action, and before review—so the returned pack is current for
that boundary. The resolver does not silently alter a pack already supplied to
an agent during a reasoning step. The next pack has a new identity and carries
the previous identity plus a refresh reason.

The manifest records `fresh`, `stale`, or `invalid`, along with generation time,
input hashes, reused entries, recalculated entries, exclusions, repository
revision, and policy/tool versions. Time-to-live is not used for tracked
repository files; it is reserved for future external providers that declare
their own freshness policy.

### Provider-neutral retrieval boundary

The resolver will define a candidate/result protocol containing query, path,
excerpt, score, authority, freshness, relationship, and provider metadata.
Future embedding or graph providers can implement that boundary without
changing the pack format or authority rules.

## Risks / Trade-offs

- [Risk] A manually maintained registry can become stale → validate paths,
  hashes, relationship targets, status values, and duplicate identities in CI.
- [Risk] SQLite FTS availability can differ across Python builds → provide a
  deterministic LIKE-search fallback and report which backend was used.
- [Risk] A bounded pack may omit useful context → record exclusions and expose
  search commands; never silently claim completeness.
- [Risk] Agents could reason over a pack while source files change → refresh at
  explicit boundaries and never replace an in-use pack invisibly.
- [Risk] Overly broad invalidation could make local work slow → invalidate by
  dependency hashes and reserve full rebuilds for explicit or incompatible
  changes.
- [Risk] Future semantic retrieval could introduce stale suggestions → require
  provenance and authority metadata on every provider result and keep it
  subordinate to deterministic context.
- [Risk] Registry metadata could expose sensitive paths → reject secrets,
  runtime state, and ignored local files during validation and indexing.

## Migration Plan

1. Add the registry schema, resolver commands, ignored generated paths, and
   tests.
2. Register the existing authority documents and active tooling boundaries.
3. Build and inspect a sample pack for a named OpenSpec change.
4. Validate preflight reuse, dependent invalidation, explicit full rebuild, and
   pack manifest evidence.
5. Regenerate the index whenever tracked metadata or relevant files change;
   deleting `.context/generated/` is the rollback path.
6. Later providers may be added behind the retrieval boundary without changing
   existing packs or authority precedence.

## Open Questions

- The semantic embedding model and provider remain intentionally undecided
  until lexical discovery shows a measurable gap.
- Whether graph traversal should remain SQLite-backed or move to a dedicated
  graph store is deferred until relationship volume and multi-hop use cases are
  measured.
