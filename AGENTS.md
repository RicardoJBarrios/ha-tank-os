# Common Agent Contract for ha-tank-os

This file defines the common rules for any agent working in this repository.
Instructions specific to a provider, IDE, skill, or model must act as adapters
to this contract; they do not create a parallel authority.

## Required context

Before proposing or modifying code, canonical documentation, or configuration,
read:

1. [`docs/vision-y-requisitos.md`](docs/vision-y-requisitos.md), the authority
   for product scope and requirements.
2. [`docs/metodologia-modelado-sdd.md`](docs/metodologia-modelado-sdd.md), the
   authority for the modeling flow, gates, and the roles of BMAD, Spec Kit, and
   OpenSpec.
3. The active PRD, architecture, ADRs, constitution, and OpenSpec change, when
   they exist.

The operational toolchain and its canonical commands are documented in
[`docs/agent-tooling.md`](docs/agent-tooling.md). Read it before selecting or
substituting linters, formatters, security tools, modeling tools, or external
services.

When the local context resolver is available, use
[`docs/context-resolution.md`](docs/context-resolution.md) and generate a
fresh context pack for the active OpenSpec change at task boundaries. Treat
packs and search results as derived aids: canonical requirements,
architecture, ADRs, and OpenSpec artifacts remain authoritative.

Before implementing a product change, run `pnpm validate:readiness --change
<change-id>`. A passing `openspec validate --all` is structural validation only;
it does not grant `Product baseline ready` or `Change ready`.

If two authorities conflict, stop, identify the affected documents, and request
correction of the owning authority. Do not silently choose a version.

## Flow and authorities

- BMAD organizes discovery, the PRD, global architecture, and the initial
  capability map.
- If adopted, Spec Kit provides the engineering constitution and compatible
  controls; it does not create a second canonical change flow.
- OpenSpec governs each bounded change and its behavioral specifications,
  design, and tasks.
- GitHub may reflect organizational status, but it does not replace canonical
  repository artifacts.
- Git preserves history and diffs, but a diff or agent assertion does not
  replace verification or human validation.
- GitHub Flow is the repository collaboration flow: `main` is the only
  long-lived branch, work uses short-lived branches, and changes merge through
  reviewed pull requests. See [`docs/github-flow.md`](docs/github-flow.md).

Do not generate parallel canonical PRDs, specifications, plans, or task lists.
Do not start product implementation without `Product baseline ready` and an
approved `Change ready` change.

## Working rules

- Always separate confirmed facts, assumptions, recommendations, pending
  decisions, and verification results.
- Keep one canonical representation of each artifact and link derived artifacts
  to their authority.
- Preserve provenance and uncertainty. Do not present examples as real Veril
  data or a proposal as the current configuration.
- Prioritize native Home Assistant capabilities before adding custom logic,
  without making HA entities or Recorder the canonical authority by default.
- Recording data must not actuate equipment by itself. Any external effect needs
  an explicit design, permissions, safeguards, and validation.
- Keep product and engineering rules provider-neutral. Codex, VS Code, BMAD,
  Spec Kit, and OpenSpec are tools in the flow, not the source of requirements.
- Write all code, technical names, comments, commit messages, and versioned
  repository documentation in English, including PRDs, architecture, ADRs, the
  constitution, and specifications. The conversation with the product owner
  may use whichever language is most useful.
- The final product must be multilingual. That is a product requirement and
  does not change the English language of its code or documentation.
- Do not install, initialize, publish, or connect external services merely as a
  consequence of reading documentation. Record each such action as a separate
  decision or request when it is needed.

## Agent-platform controls

- Agent-platform changes MUST use the local trace boundary for run identity,
  provenance, events, and evidence references when an execution run exists.
- Tool adapters MUST evaluate operations through the explicit policy boundary
  before execution and MUST treat `require_approval` as non-executable.
- Retry behavior MUST use the reliability policy and MUST remain restricted to
  explicitly idempotent transient failures.
- Automated evaluations and governance checks are evidence, not product-owner
  acceptance. Missing evidence fails closed.
- Derived artifacts MUST retain lineage manifests and MUST NOT replace canonical
  requirements or architecture.
- `pnpm quality:checks` is the CI-equivalent gate and includes `pnpm
  test:python`; do not bypass the test suite by running only static checks.
- Codex sessions MUST run `pnpm agent:codex:self-test` before enabling strict
  hook mode. Audit mode is not enforcement; strict mode is only valid after
  the selected Codex client has been exercised with real payloads.

## Evidence and delivery

Before delivering a change:

- run applicable validations and retain commands, versions, results, and
  relevant limits;
- distinguish technical verification from product-owner validation;
- review scope and do not include unauthorized work;
- do not push directly to `main` or create a parallel `develop` branch;
- run `git diff --check` when versioned files change; and
- link the delivery to the documents and scenarios that justify it.

Product acceptance and scope decisions belong to the product owner. The agent
may propose, check, and identify risks, but may not approve them on the owner's
behalf.
