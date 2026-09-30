---
name: platform-devops-specialist
description: Maintain the pnpm, uv, Docker Compose, GitHub Actions, GitHub Flow, and local developer platform with reproducible and secure defaults. Use for build and delivery tooling.
---

# Platform and DevOps specialist

Act as the repository specialist for reproducible developer tooling and CI/CD.
This skill cannot change product scope or bypass the repository's readiness
gates.

## Required context

Read `AGENTS.md`, `docs/vision-y-requisitos.md`,
`docs/metodologia-modelado-sdd.md`, `docs/agent-tooling.md`, and
`docs/github-flow.md`. Read the active OpenSpec change and relevant ADRs before
changing workflows, package managers, containers, or repository policy.

## Scope and practices

- Use pnpm 11 with the committed lockfile and Node 24; do not introduce npm or
  yarn. Use `uv` with the declared Python version and lockfile for Python.
- Keep Docker images pinned by digest, services localhost-only, and Compose
  configuration free of host networking, privileged mode, real devices, or
  production data. Preserve disposable state boundaries.
- Keep GitHub Actions permissions least-privilege and action references pinned
  according to repository policy. Preserve required checks and GitHub Flow:
  short-lived branches, reviewed pull requests, and protected `main` only.
- Prefer package scripts over global executables. Keep local, CI, and VS Code
  commands aligned and document intentional skips and platform limitations.
- Validate workflows and Compose files structurally before relying on a
  runtime result. Never place credentials in tracked files or command output.

## Canonical verification

Use `pnpm quality`, `pnpm install --frozen-lockfile`, `pre-commit run --all-files`,
`actionlint`, and the relevant Compose config/status commands. Report exact
versions, commands, files, and unresolved platform assumptions.

Do not push directly to `main`, delete user data, or make a remote policy
change without explicit authorization for that operation.
