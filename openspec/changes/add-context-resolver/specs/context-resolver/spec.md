# Spec Delta

## Purpose

The context resolver gives agents a bounded, authoritative, and reproducible
view of the repository for an active change without treating semantic search
or stale history as a source of truth.

## ADDED Requirements

### Requirement: The resolver SHALL represent artifact authority and relationships

The context system SHALL represent the path, artifact kind, authority status,
freshness status, and explicit relationships of relevant repository artifacts.
It SHALL distinguish canonical, derived, historical, and local-generated
artifacts and SHALL preserve relationship direction and provenance.

#### Scenario: A canonical specification is registered

- **WHEN** the registry is validated for a current OpenSpec specification
- **THEN** the validator reports its path, capability identity, canonical
  status, and authority precedence without duplicating its contents

#### Scenario: A superseded artifact is discovered

- **WHEN** an artifact is marked as superseded by another artifact
- **THEN** normal context resolution excludes it unless the request explicitly
  asks for historical evidence, and the output identifies the replacement

### Requirement: The resolver SHALL build deterministic context packs

The resolver SHALL build a context pack for an active bounded change from
mandatory project instructions, the active change artifacts, and explicitly
linked specifications, decisions, source paths, and tests. The pack SHALL list
every included and excluded artifact with its reason, source path, authority
status, and content hash.

#### Scenario: A pack is built for an active change

- **WHEN** an operator requests a context pack for a named active change
- **THEN** the resolver includes the required authority files and reachable
  linked artifacts in stable order and writes a manifest with hashes

#### Scenario: The requested change does not exist

- **WHEN** an operator requests a pack for an unknown change
- **THEN** the command fails without creating a misleading pack and reports the
  missing change name

#### Scenario: A context budget is reached

- **WHEN** linked artifacts exceed the configured pack budget
- **THEN** the resolver keeps mandatory and higher-authority artifacts first,
  records excluded lower-priority artifacts, and fails if mandatory material
  cannot fit

### Requirement: The resolver SHALL track freshness and recalculate incrementally

The resolver SHALL identify indexed artifacts and context packs by content
hash, registry hash, resolver version, authority-policy hash, repository
revision when available, change identity, task identity, and relevant
dependency hashes. It SHALL reuse unchanged indexed material and SHALL
recalculate only affected entries unless a rebuild is explicitly requested or
the index schema or resolver version is incompatible.

#### Scenario: An unrelated file changes

- **WHEN** a file outside the active change's reachable dependencies changes
- **THEN** the next preflight keeps the existing index entries and context pack
  content for the active change fresh without rebuilding them

#### Scenario: A linked dependency changes

- **WHEN** a linked specification, ADR, source path, or test changes
- **THEN** the next preflight marks the affected index entry and dependent pack
  stale and recalculates those entries before returning a fresh pack

#### Scenario: A full rebuild is requested

- **WHEN** the operator passes the documented rebuild option
- **THEN** the resolver discards derived index state, rebuilds it from tracked
  inputs, and records that an explicit full rebuild caused the refresh

### Requirement: Refresh behavior SHALL be transparent at defined boundaries

The resolver SHALL perform a cheap freshness preflight at context-pack
generation and SHALL support explicit refresh before mutable actions, review,
or task transitions. It SHALL NOT silently replace the context of an active
agent reasoning step; a new pack SHALL be identified as a new version.

#### Scenario: A pack is still fresh

- **WHEN** preflight compares the current input identities with the cached pack
- **THEN** the resolver reuses the pack and reports the cache key and reuse
  reason

#### Scenario: A pack is stale

- **WHEN** preflight detects a changed or missing input
- **THEN** the resolver refreshes the affected material before returning the pack
  and reports each refresh reason

#### Scenario: A required input is missing or contradictory

- **WHEN** preflight cannot resolve a mandatory dependency or detects an
  authority contradiction
- **THEN** the resolver returns `invalid`, identifies the affected input, and
  does not present the pack as current

### Requirement: Context packs SHALL expose their reuse and refresh evidence

Every generated or reused pack SHALL include its generation time, freshness
state, cache key, resolver version, repository revision when available, input
hashes, reused entries, recalculated entries, excluded entries, and the reasons
for any refresh or invalidation.

#### Scenario: An agent receives a reused pack

- **WHEN** a fresh cached pack is returned
- **THEN** its manifest states that it was reused and identifies the unchanged
  inputs that justified reuse

#### Scenario: An agent receives a refreshed pack

- **WHEN** one or more dependencies changed
- **THEN** its manifest identifies the changed hashes, recalculated entries,
  previous pack identity, and new pack identity

### Requirement: The resolver SHALL provide authority-aware lexical discovery

The resolver SHALL provide local lexical search over indexed repository text as
a discovery fallback. Search results SHALL expose authority, freshness,
relationship, and path metadata and SHALL never silently override the
deterministic context pack.

#### Scenario: An agent searches for a domain term

- **WHEN** the agent searches the local index for a term or symbol
- **THEN** the command returns ranked text matches with source paths, excerpts,
  authority status, and an explicit indication that results are discovery
  candidates rather than mandatory context

#### Scenario: Search finds an archived match

- **WHEN** lexical search finds a matching archived or superseded artifact
- **THEN** the result is labeled as historical and is ranked below current
  authoritative material unless historical search is explicitly requested

### Requirement: The derived index SHALL be local, regenerable, and disposable

The index SHALL be stored in a repository-ignored local SQLite file or an
equivalent local derived file. It SHALL be rebuildable from versioned files and
metadata, SHALL not contain credentials or runtime Home Assistant state, and
SHALL not become canonical domain persistence.

#### Scenario: The index is rebuilt on a clean machine

- **WHEN** an operator runs the documented index command after installing the
  repository dependencies
- **THEN** the same tracked inputs produce the same schema and stable metadata
  regardless of whether a previous local index existed

#### Scenario: Local generated state is removed

- **WHEN** the operator deletes the derived index and generated packs
- **THEN** the repository remains usable and the index and packs can be
  regenerated without losing canonical artifacts

### Requirement: The context system SHALL define an extension boundary for richer retrieval

The resolver SHALL expose a retrieval boundary that permits future semantic
search and graph traversal providers to contribute candidates with provenance,
authority, freshness, and relevance metadata. Such providers SHALL remain
optional and SHALL not change authority precedence or deterministic inclusion
rules.

#### Scenario: No semantic provider is configured

- **WHEN** the resolver builds a pack or performs discovery without an optional
  semantic provider
- **THEN** deterministic links and local lexical search continue to work

#### Scenario: A semantic provider returns a stale match

- **WHEN** an optional provider returns a stale or superseded artifact
- **THEN** the resolver labels it, applies authority filtering, and prevents it
  from displacing current mandatory or linked context

### Requirement: Context operations SHALL protect sensitive material

The resolver SHALL exclude secrets, tokens, local Home Assistant state,
database files, generated reports, and ignored files by default. It SHALL
redact sensitive values in diagnostics and SHALL report the exclusion policy in
the pack manifest.

#### Scenario: A local secret-like file is encountered

- **WHEN** indexing or packing encounters an ignored secret, token, or runtime
  state path
- **THEN** the resolver excludes it and does not copy its contents into the
  index, search output, or context pack
