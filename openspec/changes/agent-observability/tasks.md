# Tasks

## 1. Derived metrics

- [x] 1.1 Implement a versioned observability snapshot over the trace store with explicit UTC window and bounded scan; verify empty and populated windows.
- [x] 1.2 Add status, duration, event-type, and safe failure classifications without raw payloads; verify deterministic aggregation and secret exclusion.
- [x] 1.3 Add JSON CLI output and English operational documentation; verify documented commands run against a temporary trace store.

## 2. Verification

- [x] 2.1 Add regression tests for truncation, malformed/incomplete runs, and schema compatibility; verify all observability tests pass.
- [x] 2.2 Run Python tests, quality checks, context validation, OpenSpec validation, and `git diff --check`; record limits and results.
