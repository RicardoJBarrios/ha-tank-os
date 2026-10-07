# Validation Evidence

## Storage and lifecycle spike

| Item | Result |
| --- | --- |
| Host Python | 3.14.6 on macOS 26.6.2 arm64 |
| Test Python environment | Python 3.14.6 |
| Home Assistant package | 2026.9.4 |
| Home Assistant container | Pinned image digest from `compose.ha.yaml`, running on Linux |
| Container readiness | `pnpm ha:up`, `pnpm ha:wait`, and `pnpm ha:status` passed; status correctly reported authentication required |
| Native persistence primitive | `homeassistant.helpers.storage.Store` with `atomic_writes=True` |
| Versioning | Store major/minor version metadata is persisted and a migration callback receives the prior version and data |
| Atomic write evidence | A successful save was reloaded from `.storage/tank_os.foundation`; a simulated atomic-write failure left the previous canonical file unchanged in the contract test |
| Migration evidence | A version `1.1` payload was migrated to version `2.1` and rewritten with the migrated data in an isolated probe |

## Decision for this change

Use Home Assistant `Store` as the storage adapter primitive behind the ha-tank-os repository boundary. The adapter enables atomic file replacement, versioned major/minor metadata, and migration callbacks. The application repository rereads the saved payload and raises a persistence error when the committed data cannot be confirmed.

This decision applies to the first product slice and is not a claim that all future data volumes or telemetry workloads should use the same mechanism. High-volume telemetry remains outside this change.

## Native Home Assistant surface evidence

- The integration exposes a normal Home Assistant config flow without declaring `single_config_entry` in the manifest.
- Multiple Tanks are represented inside the canonical repository; the integration configuration is not the Tank model.
- Native services provide structured responses for Tank/context creation and retrieval and route mutations through the application service.
- Contract tests verify that a Home Assistant user context is required for mutations and that no custom frontend is needed for the first context workflow.

## Limits

- The tested Home Assistant version is the repository's pinned development line, not a declared product compatibility range.
- The black-box container proves lifecycle availability only; it does not authenticate a product user or prove the integration behavior.
- Backup restoration, multi-process concurrency, and high-volume telemetry retention are not validated by this spike.

## Implementation verification

- `pnpm test:python`: 48 tests passed.
- `pnpm lint:markdown`: passed.
- `pnpm lint:planning`: passed with 0 issues.
- `pnpm lint:spelling`: passed.
- `pnpm lint:python`: passed.
- `pnpm format:python:check`: passed.
- `pnpm typecheck:python`: passed with mypy 1.18.2.
- `pnpm lint:frontend`: passed.
- `pnpm format:frontend:check`: passed.
- `pnpm audit --audit-level=high`: no known vulnerabilities.
- Python security scan: no issues identified.
- OpenSpec validation: 13 changes passed.
- Product baseline readiness: ready.
- `git diff --check`: passed.

The implementation review found no discrepancy requiring an update to the
approved PRD, capability map, architecture spine, or this change's
specifications. Product-owner validation remains separate from these technical
results.

## Review preparation and verification refresh — 2026-10-07

The review target is implementation commit `5a3f780`, compared with planning
commit `e3479f6`: 18 changed files, 1,569 insertions, and 22 deletions. The local
competitive-research supplement is outside that implementation diff.

Environment: Node 24.18.0, pnpm 11.17.0, Python 3.14.6, pytest 9.0.3,
uv 0.11.32, and pre-commit 4.6.1 on macOS.

| Command | Current result |
| --- | --- |
| `pnpm context:pack --change establish-aquarium-observation-foundation` | Fresh derived context pack generated |
| `pnpm validate:readiness --change establish-aquarium-observation-foundation` | Ready; implementation authorization only |
| `pnpm quality` | Failed at the JavaScript dependency audit after all 48 Python tests, Markdown/planning/spelling checks, Python lint/format/types, and frontend lint/format passed |
| `pnpm audit --json` | One high, one moderate, and one low advisory in development dependencies |
| `pnpm security:python` | Passed; no issues identified |
| `pnpm security:python:dependencies` | Skipped by the canonical script because no product requirements file exists; this is not a clean test-environment dependency audit |
| `pnpm validate:openspec` | All 13 changes passed structural validation |
| `pnpm security:secrets` | Passed; no leaks found |
| `pre-commit run --all-files` | All nine hooks passed |
| `git diff --check` | Passed |

The blocking advisory is
[GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm)
for `braces` 3.0.3, used through OpenSpec and Markdown tooling. The audit reports
a patched range of `>=3.0.4`, but `pnpm view braces versions --json` returned
versions only through 3.0.3. `pnpm update braces --depth Infinity` completed
without changing the dependency or lockfile. A compatible remediation therefore
remains unresolved in the queried registry. The other reported packages are
`smol-toml` 1.8.0 (moderate) and `katex` 0.16.47 (low). No advisory was
suppressed, and the full quality gate remains failed.

Independent review has not run. The local PreToolUse hook rejected the first
reviewer launch with `unknown Codex tool` for `collaborationspawn_agent`. The
BMAD review workflow's fallback package contains four self-contained reviewer
prompts, the commit narrative, and a source-hash lineage manifest under the
ignored local directory
`_bmad-output/implementation-artifacts/artifacts/observation-review-2026-10-07/`.
These are handoff inputs, not review findings or acceptance evidence.

No interactive owner-validation session or new Home Assistant compatibility
exercise was performed during this refresh. At the end of that refresh,
independent review, dependency remediation, and product-owner validation were
outstanding. No pull request had been opened and the change had not been
archived.

## Product-owner validation and delivery preparation — 2026-10-07

The product owner explicitly confirmed validation in the conversation and
instructed the agent to continue. This records owner acceptance of the first
aquarium-observation foundation implemented in `5a3f780`. No additional
scenario-execution report was supplied with that confirmation.

Owner acceptance does not close independent review or the failing dependency
gate. A fresh `pnpm security:dependencies` still reports the high-severity
`braces` advisory. `pnpm agent:codex:self-test` reports a valid configuration in
audit mode, with no collaboration tool in its controlled-tool list; it does
not establish successful reviewer execution or strict runtime enforcement.

Delivery is prepared as two dependent draft pull requests because `main`
contains only the initial repository commit:

- The development-environment prerequisite contains the existing commits
  through `e0174bd` and targets `main`.
- The product baseline and observation foundation contain the subsequent
  planning, implementation, and evidence updates and target the prerequisite
  branch. After the prerequisite merges, this pull request must target `main`
  and pass its required checks and review before merging.

The separate uncommitted competitive-research supplement is not part of this
delivery. The OpenSpec change remains active while independent review and
technical delivery gates are unresolved.

## Draft delivery and CI follow-up — 2026-10-07

The delivery is published as dependent drafts:

- [Development environment, PR #1](https://github.com/RicardoJBarrios/ha-tank-os/pull/1).
- [Product baseline and foundation, PR #2](https://github.com/RicardoJBarrios/ha-tank-os/pull/2).

The first product CI run
([37691322697](https://github.com/RicardoJBarrios/ha-tank-os/actions/runs/37691322697))
passed all 48 tests on Linux and macOS before the dependency audit failed.
The secret scan passed. Windows failed before test collection because the Home
Assistant pytest plugin imported the POSIX-only `fcntl` module. The browser
job could not resolve a misspelled `actions/setup-node` commit reference.

The prerequisite fixes the action reference to the officially verified commit
`49933ea5288caeca8642d1e84afbd3f7d6820020`, and disables only the Home Assistant
pytest plugin on native Windows. The product tests explicitly skip their 11
Home Assistant runtime cases on Windows and defer runtime imports there.
Portable tests still run on Windows; Linux and macOS retain all runtime tests
and their existing assertions. This defines test execution boundaries, not
native Windows Home Assistant runtime support.

Local verification of the correction: `actionlint` 1.7.12, frontend lint and
formatting, Markdown/spelling checks, Python lint/formatting, and
`git diff --check` passed. `pnpm test:python` passed all 37 prerequisite tests
in its isolated worktree and all 48 product-checkout tests on macOS.
`pre-commit run --all-files` and the prerequisite commit hooks passed.
The prerequisite's full `pnpm quality` gate still fails at the same dependency
audit; Windows execution and the browser job require confirmation from the
updated CI run.
