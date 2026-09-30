# Agent Run Traceability

The repository has a local, provider-neutral trace store for agent executions. It records run lifecycle, ordered events, reproducibility references, and evidence locators without becoming product persistence or Home Assistant Recorder.

## Storage boundary

The default SQLite store is `.agent-state/trace.sqlite3`, which is ignored by Git. Set `AGENT_TRACE_STORE` or pass `--store` to use another local path. The store is operational evidence and can be removed or exported independently of product data.

The trace does not contain full source files, Home Assistant state, credentials, or complete provider transcripts by default. Context packs and canonical repository documents remain authoritative for requirements and source context.

## Commands

Start a run:

```bash
pnpm agent:trace -- start --agent-id developer --provider local --model development --change-id agent-run-traceability --task-id 1.1
```

The command prints a JSON object containing `run_id`. Use that identifier for subsequent operations:

```bash
pnpm agent:trace -- event RUN_ID tool.completed --payload '{"tool":"pytest","result":"passed"}'
pnpm agent:trace -- reference RUN_ID artifact artifacts/agent-run.json --verification-status unverified
pnpm agent:trace -- inspect RUN_ID
pnpm agent:trace -- verify RUN_ID
pnpm agent:trace -- export RUN_ID > artifacts/agent-run.json
pnpm agent:trace -- finish RUN_ID succeeded --reason "Validated locally"
```

References can also be added through the Python API when structured metadata is required:

```python
from agent_platform.trace import TraceStore

store = TraceStore()
store.add_reference(
    run_id,
    "context-pack",
    ".context/generated/packs/agent-run-traceability.json",
    verification_status="verified",
    metadata={"cache_key": "..."},
)
```

Recover an explicitly stale run without deleting its evidence:

```bash
pnpm agent:trace -- recover RUN_ID --stale-after-seconds 3600 --reason "Local process interrupted"
```

## Redaction and integrity

Redaction happens before an event is persisted and again at export boundaries. Sensitive field names, authorization headers, common token formats, credentials, and configured secret-like values are replaced with `[REDACTED]`; the original value is never retained in the trace.

Events are append-only and chained with SHA-256 over canonical JSON. `verify` recomputes the chain and reports the first inconsistent sequence. This is tamper-evident integrity, not an external authenticity signature.

## Failure limits and retention handoff

SQLite writes use a bounded local busy timeout. A busy or corrupted store is an operational failure and must not be treated as product-state evidence. Export useful traces before cleanup, and retain the export alongside the relevant change evidence when a run explains a decision or validation result.

The later permissions, privacy/retention, observability, and evidence-lineage changes will define their own controls on top of this store. They must not weaken pre-persistence redaction or reinterpret the trace as the product's canonical data store.
