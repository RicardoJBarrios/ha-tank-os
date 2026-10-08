# Agent Toolchain Contract

This document is the operational index for agents working in `ha-tank-os`. It
does not replace the product requirements, methodology, PRD, architecture,
constitution, or OpenSpec change authorities. It explains which tools exist,
which command is canonical, and which boundaries agents must preserve.

## Authority and workflow

| Concern | Canonical authority | Tool role |
| --- | --- | --- |
| Product scope and requirements | `docs/vision-y-requisitos.md` | Input to BMAD |
| Modeling flow and readiness gates | `docs/metodologia-modelado-sdd.md` | Shared process contract |
| Product definition and global architecture | Approved BMAD PRD, architecture, and ADRs | BMAD discovery and design |
| Engineering principles | `.specify/memory/constitution.md`, only after owner approval | Spec Kit controls |
| Current behavior | `openspec/specs/` | OpenSpec specifications |
| Bounded work | `openspec/changes/<change>/` | OpenSpec proposal, design, tasks, and evidence |
| Agent operating rules | `AGENTS.md` | Shared instructions for every compatible agent |

Never create a parallel PRD, architecture, specification, plan, or task list.
Do not implement product behavior before `Product baseline ready` and an
approved `Change ready` change. Enforce the latter with
`pnpm validate:readiness --change <id>`; OpenSpec structural validation alone is
not sufficient.

## Canonical commands

Run commands from the repository root.

| Purpose | Command | Guardrail |
| --- | --- | --- |
| Install Node tooling | `pnpm install --frozen-lockfile` | Use the committed lockfile; do not use npm or yarn |
| Complete local gate | `pnpm quality` | Includes the local gitleaks scan |
| CI-equivalent gate | `pnpm quality:checks` | Runs Python tests plus static, dependency, OpenSpec, and diff checks; CI runs it and keeps gitleaks in its dedicated job |
| Python lint | `pnpm lint:python` | Ruff configuration is in `ruff.toml` |
| Python formatting check | `pnpm format:python:check` | Ruff is the formatter and import organizer |
| Python type check | `pnpm typecheck:python` | Uses `pyproject.toml`; skips until product sources exist |
| Frontend lint | `pnpm lint:frontend` | Neutral ESLint flat config until a framework is approved |
| Frontend formatting check | `pnpm format:frontend:check` | Prettier configuration is in `.prettierrc.json` |
| Node dependency audit | `pnpm security:dependencies` | Fails on high or critical advisories |
| Python code security | `pnpm security:python` | Bandit uses `pyproject.toml`; skips generated tooling |
| Python dependency security | `pnpm security:python:dependencies` | Activates when project requirements files exist |
| HA test dependency security | `pnpm security:python:test-environment` | Audits the pinned test stack; may expose upstream HA pins |
| Secret scan | `pnpm security:secrets` | Scans repository content; excludes only local `.venv` and HA runtime state |
| OpenSpec validation | `pnpm validate:openspec` | Uses the repository-local OpenSpec dependency |
| Planning-document lint | `pnpm lint:planning` | Lints generated BMAD Markdown when `_bmad-output` exists; skips cleanly before product work starts |
| Readiness status | `pnpm validate:readiness` | Reports whether the product baseline is not started or ready; does not authorize implementation |
| Required change gate | `pnpm validate:readiness --change <id>` | Fails closed unless the approved baseline and bounded OpenSpec change are ready |
| Pre-commit checks | `pre-commit run --all-files` | Hooks must remain aligned with package scripts |
| Start local SonarQube | `pnpm sonarqube:up` | Local-only Docker service; never put tokens in the repository |
| Check local SonarQube | `pnpm sonarqube:status` | Uses the unauthenticated local system-status API |
| Stop local SonarQube | `pnpm sonarqube:down` | Named volumes are intentionally persistent |
| Start Home Assistant test target | `pnpm ha:up` | Local-only, pinned container; no host networking or devices |
| Wait for Home Assistant | `pnpm ha:wait` | Checks readiness only; does not authenticate or prove compatibility |
| Check Home Assistant status | `pnpm ha:status` | Accepts the expected unauthenticated HTTP 401 response |
| Check Home Assistant MCP | `pnpm ha:mcp:status` | Requires user-owned `HA_TEST_TOKEN`; never prints the token |
| Run Python tests | `pnpm test:python` | Uses the project `uv` environment; this is also part of `pnpm quality:checks` |
| Run browser E2E tests | `pnpm test:e2e` | Starts only after HA readiness; writes HTML/JUnit and failure evidence |
| Run headed browser E2E | `pnpm test:e2e:headed` | Useful for interactive diagnosis; still uses the isolated HA target |
| Open browser report | `pnpm test:e2e:report` | Serves the local Playwright HTML report |
| Stop Home Assistant test target | `pnpm ha:down` | Stops only this repository's Compose service |
| Validate context registry | `pnpm context:validate` | Checks authority metadata and safe paths |
| Build context index | `pnpm context:index` | Incrementally updates ignored local SQLite state |
| Search context candidates | `pnpm context:search -- <term>` | Discovery only; never replaces authority |
| Build context pack | `pnpm context:pack -- --change <name>` | Reuses fresh packs and records refresh evidence |
| Record an agent run | `pnpm agent:trace -- start ...` | Creates the local run boundary; finish or recover it explicitly |
| Inspect agent observability | `pnpm agent:observability -- --start <UTC> --end <UTC>` | Reads bounded metrics from the local trace without raw payloads |
| Validate Codex runtime hooks | `pnpm agent:codex:self-test` | Verifies hook coverage, Windows launchers, and the controlled-tool registry before strict mode |
| Check agent runtime readiness | `pnpm agent:health` | Redacted, non-mutating check of hooks, Home Assistant MCP, and local SonarQube when available |

Agent-platform modules are exercised together by the Python suite, which is
part of `pnpm quality:checks`. Tool adapters must still call policy and
reliability decisions at their execution boundary; the modules do not grant
implicit permissions or execute operations themselves.

Git collaboration follows [GitHub Flow](./github-flow.md): `main` is the only
long-lived branch, changes use short-lived branches and pull requests, and
remote branch protection is configured on GitHub rather than inferred from a
local checkout.

When a command is represented by a package script, use the package script
instead of invoking a global executable directly. This keeps local, VS Code,
and CI behavior aligned.

The context resolver and its freshness policy are documented in
[context-resolution.md](./context-resolution.md). Agents should build or
refresh a pack at task boundaries when an active OpenSpec change is available,
but must still read the canonical authority files directly and must not treat
lexical, semantic, or graph discovery as authoritative.

## Tool-specific rules

### Python

- Ruff is the canonical linter, formatter, and import organizer. Do not add
  Black or isort unless an approved architecture decision requires them.
- mypy, Bandit, pytest, and pip-audit are installed through `uv` as standalone
  tools. Their shared policy is in `pyproject.toml`.
- Product Python is expected under `src/` or `custom_components/`; tests belong
  under `tests/`. Generated BMAD, Spec Kit, and OpenSpec Python files are not
  product code and must not be modified to satisfy project lint rules.
- Home Assistant compatibility is not claimed until an integration manifest,
  supported version range, and executable tests exist.
- The local Home Assistant test target is defined in `compose.ha.yaml` and uses
  a pinned multi-architecture image digest. Its state lives under
  `.docker/ha/config/` and is ignored except for the minimal tracked
  `configuration.yaml`.
- The Python test extra pins Home Assistant and
  `pytest-homeassistant-custom-component` to the same release line used for
  local integration tests. Keep the container image and Python package aligned
  unless a change explicitly records the reason for divergence.
- `requirements-dev.txt` is the disposable test environment, not a shipped
  product dependency set. Its audit is explicit and separate because upstream
  Home Assistant may pin a vulnerable transitive package before a compatible
  release is available. Never suppress such a finding silently.
- Treat container availability, Python imports, integration behavior,
  and product acceptance as separate gates. Do not report one as proof of the
  others.
- Playwright is the canonical browser E2E runner. It uses Chromium initially,
  retains screenshots, videos, and traces only for failed tests, and emits HTML
  and JUnit reports under ignored `artifacts/playwright/`.
- Keep environment smoke tests separate from product acceptance tests. Add
  visual snapshots only after the product UI, viewport, fonts, and locale are
  stable; review snapshot changes as evidence.

### Frontend

- ESLint and Prettier are installed locally through pnpm.
- The current configuration is framework-neutral. Do not add Angular, React,
  Vue, Lit, or TypeScript-specific plugins before the product baseline selects a
  frontend boundary.
- The product vision currently prefers native Home Assistant UI and treats
  TypeScript + Lit as an option, not a decision.

### SonarQube

- SonarQube Community Build is an optional local analysis server defined in
  `compose.sonar.yaml` and bound to `127.0.0.1:9000`.
- The Web API and scanner are the canonical automation interfaces. A SonarQube
  MCP is not required for analysis or quality gates; it is only useful for
  conversational querying of issues and measures.
- `pnpm agent:health` probes the local `127.0.0.1:9000` endpoint by default and
  uses `SONAR_HOST_URL` only when a remote or non-default server is intended.
- The project-specific SonarQube project and analysis token remain pending
  until product source roots and ownership are approved. Never reuse the
  existing global Sonar MCP configuration for another repository.
- SonarLint/SonarQube findings are additional evidence. They do not replace
  Ruff, ESLint, Prettier, tests, gitleaks, or the product-owner gates.
- Do not configure a shared SonarQube/SonarCloud connection or commit tokens
  until the project identity and credential ownership are approved.

### Home Assistant MCP

- The local Docker instance uses Home Assistant's official MCP Server
  integration and the built-in Assist API endpoint
  `http://127.0.0.1:8123/api/mcp/assist`.
- Codex reads the token from the user-owned `HA_TEST_TOKEN` environment
  variable. Never copy the token into `.codex/config.toml`, documentation,
  reports, tests, or shell history.
- `pnpm ha:mcp:status` performs only the MCP initialize handshake. Use it as a
  transport/authentication check, not as proof of product behavior.
- MCP exposes both read and control tools. Agents must use read-only tools for
  inspection and testing unless the product owner explicitly authorizes a
  control operation against the disposable local instance.

### BMAD, Spec Kit, and OpenSpec

- BMAD owns discovery, the PRD, global architecture, and the initial capability
  map.
- Spec Kit provides only an approved engineering constitution and compatible
  controls. Its complete change flow must not run beside OpenSpec.
- OpenSpec owns bounded changes, specifications, designs, tasks, and their
  lifecycle.
- The generated skills under `.agents/skills/` are adapters. They must respect
  `AGENTS.md` and this contract rather than inventing repository policy.
- The repository-local `ha-test-environment` skill adds safe lifecycle and
  reporting rules for the Home Assistant test target.

### Technical specialist delegation

The repository exposes narrow technical specialists as both agent skills and
VS Code agents. They advise and execute within an approved OpenSpec change;
they do not create a second product, architecture, or change authority.

| Specialist | VS Code agent | Skill | Primary scope | Explicit non-scope |
| --- | --- | --- | --- | --- |
| Home Assistant | `.github/agents/home-assistant-specialist.agent.md` | `.agents/skills/home-assistant-specialist/` | Core architecture, integrations, config entries, devices/entities, services, automations, APIs, frontend boundaries, compatibility, security, tests, operations, local MCP | Product requirements, global architecture, production control |
| Testing and E2E | `.github/agents/testing-e2e-specialist.agent.md` | `.agents/skills/testing-e2e-specialist/` | pytest, HA fixtures, Playwright, regression, failure evidence | Product acceptance, hidden flakes, weakening assertions |
| Platform and DevOps | `.github/agents/platform-devops-specialist.agent.md` | `.agents/skills/platform-devops-specialist/` | pnpm, uv, Docker Compose, CI, GitHub Flow | Product scope, unapproved remote policy changes |
| Security and Quality | `.github/agents/security-quality-specialist.agent.md` | `.agents/skills/security-quality-specialist/` | SonarQube, audits, secrets, static analysis, quality gates | Risk acceptance, silent suppressions, product approval |
| Python | `.github/agents/python-specialist.agent.md` | `.agents/skills/python-specialist/` | Python syntax, typing, async behavior, packaging, tests, security | Product scope, Home Assistant architecture |
| TypeScript and JavaScript | `.github/agents/typescript-javascript-specialist.agent.md` | `.agents/skills/typescript-javascript-specialist/` | Language quality, Node/frontend code, accessibility, localization, browser safety | Framework selection, product UX decisions |

BMAD remains the entry point for discovery, product definition, and global
architecture. BMAD Developer delegates implementation details to one primary
specialist when a change crosses that domain; BMAD Reviewer delegates
independent test or security review after implementation. Avoid concurrent
edits to the same canonical artifact by multiple specialists. Every specialist
must reread `AGENTS.md`, the active OpenSpec change, and the relevant authority
before acting, then hand back exact evidence and unresolved decisions.

## Verification and reporting

Every agent must report:

1. The exact commands it ran.
2. Tool versions when they affect the result.
3. Whether a check passed, failed, or was intentionally skipped.
4. The difference between technical verification and product-owner validation.
5. Any unresolved decision or compatibility limit.

Never describe a skipped check as a passing implementation test. Never turn a
local SonarQube result, a generated artifact, or an agent assertion into proof
of Home Assistant compatibility.
