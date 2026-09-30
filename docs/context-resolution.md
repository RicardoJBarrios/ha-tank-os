# Agent Context Resolution

The repository uses a deterministic context resolver to give agents a bounded
view of the authoritative material for an active OpenSpec change. It is a
developer-tooling capability, not product persistence and not a replacement
for requirements, architecture, ADRs, BMAD, or OpenSpec.

## Authority and retrieval order

The resolver follows this order:

1. Mandatory project instructions and current product authorities.
2. The active OpenSpec change and its reachable linked artifacts.
3. Current source and tests explicitly linked to the change.
4. Local lexical discovery results.
5. Optional future semantic or graph-provider results.

Discovery results are candidates only. They cannot override a current
canonical artifact, and historical or superseded artifacts are excluded from a
normal context pack.

Relationships and artifact metadata are versioned in
[`.context/registry.json`](../.context/registry.json). The registry identifies
paths, artifact kinds, authority, freshness, tags, and directed relationships;
it does not duplicate document contents.

## Commands

Run these commands from the repository root:

```bash
pnpm context:validate
pnpm context:index
pnpm context:search observation
pnpm context:pack --change add-context-resolver
pnpm context:pack --change add-context-resolver --rebuild
```

`context:validate` checks registry paths, relationships, authority values, and
sensitive-path exclusions. `context:index` incrementally updates the local
SQLite index. `context:search` is lexical discovery and labels its output as
non-authoritative. `context:pack` performs freshness preflight and writes a
Markdown pack plus JSON manifest under ignored `.context/generated/packs/`.

## Freshness and reuse

Tracked repository files do not use a time-to-live. Freshness is derived from
content hashes, registry metadata, resolver version, authority policy, the
active change, the requested task, and the reachable dependency set.

- Unchanged sources and packs are reused.
- A changed linked source invalidates that source and dependent packs.
- An unrelated source does not trigger a full rebuild.
- `--rebuild` explicitly discards derived index state.
- Schema or resolver-version incompatibility also causes a full rebuild.

Refresh happens at explicit boundaries: pack generation, task start, before a
mutating action, and before review. A pack already supplied to an agent is not
silently replaced during the agent's reasoning step. Every manifest records
whether the result was fresh, stale, or invalid, plus the cache key, hashes,
reused entries, recalculated entries, exclusions, and refresh reason.

## Storage and privacy

The SQLite database and generated packs are disposable. They can be deleted
and regenerated from tracked repository files. The resolver excludes secrets,
tokens, Home Assistant runtime state, generated reports, databases, ignored
paths, and local credentials. It never reads the local Home Assistant MCP
token into a pack.

The current implementation uses Python's standard-library `sqlite3`. It uses
SQLite FTS5 when available and falls back to deterministic `LIKE` search when
it is not. No Docker database or hosted retrieval service is required.

## Future semantic and graph retrieval

The resolver has a provider-neutral candidate boundary for future embeddings or
graph traversal. Such providers must return source path, excerpt, relevance,
authority, freshness, relationship, and provider metadata. They remain
optional and subordinate to deterministic context. A vector database or graph
database should be introduced only after lexical retrieval and explicit links
show a measured discovery gap.
