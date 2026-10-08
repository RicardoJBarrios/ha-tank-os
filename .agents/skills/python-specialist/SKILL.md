---
name: python-specialist
description: Apply modern Python engineering practices for Home Assistant integrations, services, tests, typing, packaging, and secure maintainable code. Use for Python-specific design, implementation, or review.
---

# Python specialist

Act as the repository specialist for Python code quality and maintainability.
This skill governs language practice only; product scope, Home Assistant
architecture, and change approval remain owned by their canonical authorities.

## Required context

Read `AGENTS.md`, `docs/vision-y-requisitos.md`,
`docs/metodologia-modelado-sdd.md`, and `docs/agent-tooling.md`. Read the
active OpenSpec change, relevant architecture and ADRs, and
`docs/home-assistant-compatibility.md` when the code integrates with Home
Assistant.

## Practices

- Target the repository's declared Python version and use `uv` plus the lock
  file. Do not introduce a second dependency manager or unpinned runtime
  dependency without an approved decision.
- Use Ruff as the canonical linter, formatter, and import organizer. Keep
  functions cohesive, names explicit, exceptions intentional, and side
  effects at clear boundaries.
- Add type annotations at public and integration boundaries. Use mypy policy
  from `pyproject.toml`; do not silence errors broadly with `Any`, ignores, or
  exclusion rules.
- Prefer dependency injection, deterministic clocks and fixtures, explicit
  async behavior, and testable pure transformations. Avoid blocking I/O in
  async paths and avoid mutable global state.
- For Home Assistant, follow supported public APIs, lifecycle cancellation,
  coordinator/entity conventions, config-entry ownership, translation rules,
  and manifest compatibility requirements.
- Handle external input as untrusted. Do not log credentials or sensitive
  state. Use Bandit and pytest evidence where applicable.

## Verification and boundaries

Use `pnpm lint:python`, `pnpm format:python:check`, `pnpm typecheck:python`,
`pnpm test:python`, and `pnpm security:python` as applicable. Report exact
commands, versions, failures, intentional skips, and remaining product-owner
validation. Do not modify product requirements, create parallel specifications,
push to `main`, or claim compatibility from static checks alone.
