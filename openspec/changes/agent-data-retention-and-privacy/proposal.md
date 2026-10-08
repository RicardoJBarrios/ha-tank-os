# Proposal

## Why

Agent traces can contain operational metadata and redacted summaries that still require clear retention limits. Privacy must be explicit so local evidence is useful without becoming an uncontrolled archive.

## What Changes

- Add sensitivity classification and retention policies for agent-platform data.
- Provide an explicit, dry-run-first purge operation for local trace runs.
- Preserve canonical repository documents and product data outside the purge boundary.

## Capabilities

### New Capabilities

- `agent-data-retention-and-privacy`: Privacy classification and controlled retention of local agent operational data.

### Modified Capabilities

None.

## Impact

- Adds a retention policy module, purge tests, and documentation.
- No automatic deletion runs by default and no product or Home Assistant data is deleted.
