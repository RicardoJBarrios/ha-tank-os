# Security Policy

## Reporting a vulnerability

Please report suspected vulnerabilities privately through the repository's
GitHub Security Advisories workflow. Do not disclose credentials, tokens,
private aquarium data, or an exploitable proof of concept in a public issue.

Include the affected version or commit, deployment context, reproduction steps,
impact assessment, and any safe mitigation that has already been tested.

## Development controls

The repository uses local secret scanning with gitleaks, dependency and action
review in CI, and protected pull requests when those GitHub controls are
available. These controls reduce risk but do not replace responsible disclosure
or product-owner validation.
