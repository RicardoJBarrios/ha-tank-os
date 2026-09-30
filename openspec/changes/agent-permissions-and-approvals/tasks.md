# Tasks

## 1. Policy evaluator

- [x] 1.1 Implement versioned explicit rules, exact operation/resource matching, deny-by-default, and stable decisions; verify allow, deny, precedence, and unknown-operation tests.
- [x] 1.2 Implement scoped, expiring, single-use approvals without persisting approval secrets; verify mismatch, expiry, and consumption tests.
- [x] 1.3 Integrate redacted decision events with the trace store; verify denied and approval-required decisions are auditable.

## 2. Delivery

- [x] 2.1 Add English documentation and a local configuration example; verify broad local access requires an explicit rule.
- [x] 2.2 Run tests, quality checks, context validation, OpenSpec validation, and `git diff --check`.
