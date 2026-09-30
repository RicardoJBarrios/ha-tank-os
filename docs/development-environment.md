# Development Environment

This repository keeps its development environment reproducible and provider
neutral. Product code, technical names, comments, commit messages, and
versioned technical documentation are written in English. The product itself
must remain multilingual; repository language is not a product-language
constraint.

## Tooling layers

- `pnpm` manages Node-based repository tooling and is pinned in
  `package.json`.
- `uv` manages standalone Python tooling and the project test environment.
  Ruff is installed as a user tool and is configured by `ruff.toml`; the test
  extra pins Home Assistant and `pytest-homeassistant-custom-component`.
- Docker Compose runs the optional local SonarQube Community Build defined in
  `compose.sonar.yaml` and the isolated Home Assistant test target defined in
  `compose.ha.yaml`; both bind to localhost only.
- Playwright runs browser E2E tests against the local HA target. Chromium is the
  initial browser; failed tests retain screenshots, videos, and traces, while
  HTML and JUnit reports are written under ignored `artifacts/playwright/`.
- BMAD owns discovery, the PRD, global architecture, and the initial capability
  map.
- Spec Kit may provide the approved engineering constitution and compatible
  controls.
- OpenSpec owns the bounded-change specifications, designs, tasks, and change
  lifecycle.
- `AGENTS.md` is the shared repository contract for all agents.

The tools do not create parallel canonical product artifacts. Product work is
still gated by `Product baseline ready` and each implementation by `Change
ready`, as defined in [the modeling methodology](./metodologia-modelado-sdd.md).

## Local commands

Install repository tooling with:

```sh
pnpm install --frozen-lockfile
```

The supported local tool floors are recorded in [`.node-version`](../.node-version)
and [`.python-version`](../.python-version). On macOS or Linux, install Node.js
24, pnpm 11.17.0, Python 3.14, uv, Docker Desktop, and pre-commit. On
Windows, use WSL2 for the Home Assistant development workflow and keep the
checkout inside the WSL filesystem; the repository quality gate itself also
runs natively on Windows in CI.

After installing the host prerequisites, run `pnpm install --frozen-lockfile`,
`pre-commit install`, and `pnpm quality`. Docker is required for the local
Home Assistant test target and optional for SonarQube.

Start the Home Assistant test target with:

```sh
pnpm ha:up
pnpm ha:wait
pnpm ha:status
```

Open `http://localhost:8123` and complete local onboarding when an authenticated
API or MCP session is required. Keep the generated user, token, `.storage`
files, database, and logs local; they are deliberately not part of the
repository. Stop the target with `pnpm ha:down`.

Validate the configured MCP bridge with:

```sh
pnpm ha:mcp:status
```

This requires `HA_TEST_TOKEN` in the user environment and performs only the
MCP initialize handshake. It does not call Home Assistant services or control
devices.

The container is an isolated black-box target, not a production-like runtime:
it uses a pinned Home Assistant image, a localhost-only port binding, no host
network, no privileged mode, no host devices, and no aquarium data. Mounting
`custom_components/` is read-only so a future integration can be tested
without allowing the container to modify source files.

Set up and run the Python test environment with:

```sh
uv sync --extra test
pnpm test:python
```

Run the browser smoke and E2E layer with:

```sh
pnpm test:e2e
pnpm test:e2e:headed
pnpm test:e2e:report
```

The current smoke case proves only that the HA onboarding or application
surface opens. Product E2E cases require an approved capability, deterministic
test data, and explicit acceptance scenarios. Authenticated browser state must
come from local environment variables or a secret store, never from committed
files.

The Python package and container image are intentionally pinned to the same
Home Assistant release line. A test run must report both versions and must
distinguish startup verification, integration behavior, and product-owner
validation.

Run the complete local quality gate with:

```sh
pnpm quality
```

Start the optional local SonarQube instance with:

```sh
pnpm sonarqube:up
```

Open `http://localhost:9000`, sign in with the initial `admin`/`admin`
credentials, and change the password immediately. Stop it with
`pnpm sonarqube:down`. The instance uses named Docker volumes so local data
survives container recreation. It is bound to localhost and is intended for
development, not production use.

Check availability with `pnpm sonarqube:status`. SonarQube automation should
use its Web API and scanner with a project-specific token stored outside the
repository. A SonarQube MCP is optional for conversational inspection only and
is not required for analysis, quality gates, or CI.

`pnpm agent:health` also detects the local server automatically. The separate
test-environment dependency audit may report vulnerabilities inherited from
the pinned Home Assistant release. For the current `2026.9.4` test line,
`pip-audit` reports advisories for `cryptography 48.0.1` and `PyJWT 2.13.0`,
while Home Assistant requires `PyJWT==2.13.0`; forcing the fixed PyJWT line
makes dependency resolution fail. This is an accepted, bounded risk for the
disposable local test environment: it does not block local development and
those packages are not shipped by the product. The audit must remain visible,
must not be presented as a clean release security result, and must be re-run
when the Home Assistant test line is upgraded.

The gate currently runs Markdown linting, English spelling checks, Ruff lint
and format checks, mypy, ESLint, Prettier, gitleaks secret scanning,
`pnpm audit --audit-level=high`, OpenSpec validation, and `git diff --check`.
Bandit and pip-audit are also wired into the gate. With no product Python code,
the product dependency audit reports an explicit skip rather than auditing the
disposable test environment. Audit that environment separately with
`pnpm security:python:test-environment`; any upstream advisory must be
reported and resolved or explicitly accepted by the product owner before it is
used for a release decision.

Install and run the Git hook checks with:

```sh
pre-commit install
pre-commit run --all-files
```

The hook configuration is local and explicit so contributors can inspect every
check. It does not rewrite files automatically.

## Visual Studio Code

The [VS Code configuration](../.vscode/) enables final-newline and whitespace
normalization, Markdown and Python formatter integration, repository exclusions
for generated caches, and tasks for the quality gate, pre-commit, and OpenSpec.
Recommended extensions are advisory; contributors may use another editor.

Agents must use the operational [agent toolchain contract](./agent-tooling.md)
for command selection, tool boundaries, and reporting requirements.

## Codex, MCP, and skills

The project-local [Codex configuration](../.codex/config.toml) registers the
public OpenAI Developer Documentation MCP without credentials and the local
Home Assistant Assist MCP endpoint. The Home Assistant token is stored only in
the user environment as `HA_TEST_TOKEN`; it must never be committed. If the
local HA state is reset, recreate the token and refresh the user environment.
Credentials for other servers must remain in user-level configuration or an
operating-system keyring and must never be committed.

The endpoint and token setup follows Home Assistant's official [MCP Server
integration](https://www.home-assistant.io/integrations/mcp_server). The
configured URL is local-only and uses the Assist API; it is not exposed outside
the Docker host.

The repository includes the installed BMAD, Spec Kit, and OpenSpec skills under
`.agents/skills/`. These are adapters to the repository contract and its
authorities, not replacements for them. The local
`ha-test-environment` skill documents the safe Home Assistant lifecycle.

## Continuous integration and security

The [quality workflow](../.github/workflows/quality.yml) runs the repository
gate on Ubuntu, macOS, and Windows and scans for leaked secrets on Ubuntu. The gate also runs
`pnpm audit --audit-level=high` against the Node dependency tree. Dependabot
monitors Node tooling and GitHub Actions. The local and CI secret scans use the
repository-specific [gitleaks configuration](../.gitleaks.toml), whose only
allowlist entry is a verified false positive in a generated BMAD manifest.

SonarQube for IDE is installed for editor feedback on Python and TypeScript.
The local Community Build in `compose.sonar.yaml` is the selected development
server. It is an additional analysis layer, not a replacement for Ruff, ESLint,
Prettier, or the repository quality gate. A CI SonarQube/SonarCloud connection
is intentionally not configured yet because that requires a shared server,
project identity, and credentials.

Home Assistant compatibility is tracked separately in
[home-assistant-compatibility.md](./home-assistant-compatibility.md). It will
become an executable CI check after the integration manifest and test layout
are approved.

VS Code extensions remain recommendations rather than pinned dependencies.
Pinning marketplace extension versions would make the editor less portable and
does not reproduce the CLI toolchain. CLI versions are pinned in
`package.json`, the lockfile, and the CI installation steps; the editor uses
the compatible current extension releases.

These controls are technical verification. They do not replace product-owner
validation, Home Assistant compatibility testing, independent review, or the
security reporting process in [SECURITY.md](../SECURITY.md).
