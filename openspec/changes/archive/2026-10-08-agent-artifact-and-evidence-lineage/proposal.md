# Proposal

## Why

Agent outputs, tests, decisions, and reports need provenance that survives handoffs and can be checked without confusing derived evidence with canonical requirements. The trace currently stores references but lacks a portable lineage manifest.

## What Changes

- Add portable artifact/evidence lineage manifests.
- Record producer run, source references, content digest, type, and verification state.
- Support verification without copying artifact contents into agent state.

## Capabilities

### New Capabilities

- `agent-artifact-and-evidence-lineage`: Provenance and verification manifests for agent-produced artifacts and evidence.

### Modified Capabilities

None.

## Impact

- Adds a local manifest builder/verifier and tests.
- Does not make derived artifacts canonical or publish them externally.
