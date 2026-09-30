# GitHub Flow

This repository uses GitHub Flow. `main` is the only long-lived integration
branch. Work is isolated in a short-lived branch and merged through a pull
request after the applicable checks and reviews pass.

## Branch lifecycle

1. Start from an up-to-date `main`.
2. Create one branch for one bounded change.
3. Keep the branch focused on its approved OpenSpec change or repository task.
4. Push the branch and open a draft pull request early when review context is
   useful.
5. Convert it to ready only when the change is reviewable and its checks pass.
6. Merge through GitHub after required review and status checks pass.
7. Delete the branch after merge and update the local `main` before the next
   change.

Do not create or maintain a `develop` branch. Do not push directly to `main`.

## Branch names

Use a short category and stable identifier:

```text
feature/<change-id>-<short-name>
fix/<change-id>-<short-name>
docs/<short-name>
test/<change-id>-<short-name>
chore/<short-name>
spike/<short-name>
```

The name is navigational metadata, not the canonical change specification.
OpenSpec remains authoritative for bounded behavior and tasks.

## Pull request contract

Every pull request must state its scope, link the relevant authority, identify
verification and pending validation, and include the exact checks run. The
author must not claim product acceptance from automated results. Reviewers
check scope, evidence, security, documentation, and compatibility boundaries.

The default merge policy is squash merge into `main`, unless preserving a
series of commits materially improves review or provenance. The final commit
message and all versioned technical documentation remain in English.

## Repository settings to enable on GitHub

These settings are external repository configuration and are not silently
changed by a local checkout:

- Protect `main` and require a pull request before merging.
- Require at least one approving review and dismiss stale approvals after new
  commits.
- Require the `quality (ubuntu-latest)`, `quality (macos-latest)`,
  `quality (windows-latest)`, and `secrets` checks.
- Require branches to be up to date before merging.
- Require conversation resolution and block force-pushes and branch deletion.
- Allow squash merge; disable merge commits unless a documented exception is
  approved.
- Restrict who can bypass the rules and keep bypass use auditable.

Until these settings are enabled, the repository files and workflows provide
guidance and automated checks but cannot enforce the remote policy.

## Local commands

```sh
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c feature/<change-id>-<short-name>
```

Before opening or updating a pull request, run `pnpm quality`, the applicable
test commands, `pre-commit run --all-files`, and `git diff --check`. A change
that affects browser behavior should also run `pnpm test:e2e`.
