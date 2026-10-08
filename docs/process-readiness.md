# Process readiness gates

The repository has two machine-checked readiness gates in addition to the
human review described in the SDD methodology.

## Product baseline

Before the first product change, create
`_bmad-output/planning-artifacts/product-baseline.yaml` after product-owner
approval. It is a status and lineage record, not a duplicate of the PRD:

```yaml
status: ready
owner_approval: approved
prd: _bmad-output/planning-artifacts/prds/<run>/prd.md
capability_map: _bmad-output/planning-artifacts/capability-map.md
architecture: _bmad-output/planning-artifacts/architecture/architecture.md
```

The linked PRD, capability map, and architecture must exist. Until this file
exists, `pnpm validate:readiness` reports `not_started` and the quality gate
remains usable for environment work. A product implementation must use the
change-specific required mode below.

## Bounded change

An approved OpenSpec change records its readiness in `.openspec.yaml`:

```yaml
schema: spec-driven
created: 2026-09-30
status: ready
owner_approval: approved
product_baseline: ready
```

The change must also contain a proposal, design, tasks, at least one spec
delta, and no unresolved `TODO`, `TBD`, or template placeholders.

Run the required gate before implementation:

```sh
pnpm validate:readiness --change <change-id>
```

The command fails closed when the product baseline or change is not ready.
`pnpm quality:checks` runs the non-required baseline check and validates any
BMAD Markdown files that already exist under `_bmad-output`.

The gate does not replace product-owner validation or independent review. It
only prevents an agent from treating incomplete planning artifacts as an
approved implementation authorization.
