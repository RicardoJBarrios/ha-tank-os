---
name: typescript-javascript-specialist
description: Apply modern TypeScript and JavaScript practices for framework-neutral frontend, Node tooling, browser automation, accessibility, localization, and secure maintainable code. Use for TypeScript or JavaScript-specific work.
---

# TypeScript and JavaScript specialist

Act as the repository specialist for TypeScript and JavaScript. Remain
framework-neutral until the product baseline selects a frontend framework.
This skill governs language practice only; product UX and architecture remain
owned by their canonical authorities.

## Required context

Read `AGENTS.md`, `docs/vision-y-requisitos.md`,
`docs/metodologia-modelado-sdd.md`, and `docs/agent-tooling.md`. Read the
active OpenSpec change and relevant architecture, UX, and ADR artifacts before
changing frontend, Node, or Playwright code.

## Practices

- Use pnpm and the repository's Node version with the committed lockfile. Keep
  TypeScript strictness, module boundaries, and compiler options explicit when
  a TypeScript project is introduced.
- Use ESLint and Prettier through repository scripts. Prefer small pure
  functions, explicit data contracts, discriminated unions, narrow types, and
  predictable async error handling. Avoid implicit `any`, unsafe casts, hidden
  global state, and unbounded event listeners.
- Keep browser code accessible and testable: semantic HTML, keyboard behavior,
  stable accessible names, explicit loading/error/empty states, and Playwright
  locators based on user-visible contracts.
- Treat all browser, URL, storage, and network input as untrusted. Avoid
  injection-prone HTML, unsafe dynamic evaluation, leaked tokens, and logging
  of sensitive values.
- Keep localization, locale, timezone, location, and metric-unit preferences
  separate. Do not hard-code display strings, date formats, or units in domain
  logic. Preserve deterministic formatting in tests.
- Keep framework-specific patterns out of neutral tooling until an approved
  architecture decision selects Angular, React, Lit, or another framework.

## Verification and boundaries

Use `pnpm lint:frontend`, `pnpm format:frontend:check`, `pnpm test:e2e`,
`pnpm security:dependencies`, and `pnpm quality` as applicable. Report exact
commands, versions, failures, intentional skips, and product-owner validation
separately. Do not change product scope, create parallel specifications, or
push to `main`.
