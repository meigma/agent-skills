---
name: github-actions
description: Create and secure GitHub Actions workflows for CI/CD automation. Use when writing workflow YAML files (.github/workflows/*.yml), configuring triggers and events, setting job dependencies and matrices, managing GITHUB_TOKEN permissions, creating reusable workflows, using third-party actions, or hardening supply chain controls such as OIDC, artifact attestations, Dependabot, dependency review, CodeQL, and runner policy.
---

# GitHub Actions

GitHub Actions automates workflows directly in your repository. Workflows are YAML files in `.github/workflows/` that run jobs in response to events.

For any workflow that crosses a trust boundary, uses tokens or secrets, publishes artifacts, or deploys to external systems, treat [security-hardening.md](references/security-hardening.md) as the canonical reference.

## Quick Reference

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
        with:
          persist-credentials: false
      - uses: actions/setup-node@<full-commit-sha>  # vX.Y.Z
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test
```

## Non-Negotiables

1. Workflows must pin every third-party action and every cross-repo reusable workflow to a full-length commit SHA.
2. Workflows must not check out or execute untrusted pull request code in `pull_request_target` or `workflow_run`.
3. Workflows must prefer `GITHUB_TOKEN`, then GitHub App installation tokens, and use PATs only as a narrow fallback.
4. Deployments and publishers must prefer OIDC or other short-lived credentials over long-lived cloud secrets.
5. Public repositories must not use self-hosted runners for untrusted pull request workloads.
6. Examples must not print tokens, secret values, or other credentials to logs.

## Reference Files

Detailed documentation organized by topic:

| Topic | File | Use When |
|-------|------|----------|
| Workflow syntax | [workflow-syntax.md](references/workflow-syntax.md) | Writing `on`, `jobs`, `steps`, `env`, `matrix`, `concurrency` |
| Events & triggers | [events-triggers.md](references/events-triggers.md) | Choosing between `pull_request`, `pull_request_target`, `workflow_run`, `schedule`, `workflow_dispatch` |
| GITHUB_TOKEN | [github-token.md](references/github-token.md) | Setting `permissions`, choosing token types, using GitHub API auth safely |
| Jobs & conditionals | [jobs-conditionals.md](references/jobs-conditionals.md) | Using `needs`, `if`, `matrix`, status functions |
| Reusable workflows | [reusable-workflows.md](references/reusable-workflows.md) | Creating/calling workflows with `workflow_call`, passing secrets and outputs |
| Using actions | [using-actions.md](references/using-actions.md) | Pinning actions, resolving SHAs, package-manager caching, Docker action references |
| TypeScript actions | [typescript-actions.md](references/typescript-actions.md) | Writing custom JavaScript/TypeScript actions with safe input handling |
| Security hardening | [security-hardening.md](references/security-hardening.md) | Trust boundaries, supply chain controls, OIDC, attestations, runners, cache/artifact safety |

## Common Patterns

### Untrusted Pull Request CI

Use `pull_request` for build and test jobs that execute contributor code. Keep permissions read-only and do not expose secrets.

```yaml
name: Pull Request CI

on:
  pull_request:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
        with:
          persist-credentials: false
      - uses: actions/setup-node@<full-commit-sha>  # vX.Y.Z
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test
```

### Privileged Deployment with OIDC

Use a protected environment and short-lived credentials for deployment jobs.

```yaml
name: Deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        required: true
        options:
          - staging
          - production

permissions:
  contents: read
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
        with:
          persist-credentials: false
      - name: Authenticate to cloud
        uses: <cloud-oidc-action>@<full-commit-sha>  # vX.Y.Z
      - run: ./deploy.sh
```

### Release Provenance

Publishing workflows should generate provenance for the artifacts they produce.

```yaml
name: Release

on:
  release:
    types: [published]

permissions:
  contents: read
  attestations: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
        with:
          persist-credentials: false
      - run: ./build.sh
      - name: Generate artifact attestation
        uses: actions/attest-build-provenance@<full-commit-sha>  # v3
        with:
          subject-path: dist/my-artifact.tar.gz
```

## Workflow Checklist

Before committing or approving a workflow change:

- [ ] Every third-party action and cross-repo reusable workflow is pinned to a full-length commit SHA
- [ ] `permissions` are explicitly set to the minimum required at workflow or job level
- [ ] Secrets are accessed via `${{ secrets.NAME }}` and never printed or echoed
- [ ] `pull_request_target` and `workflow_run` do not check out or execute untrusted code
- [ ] OIDC is used instead of long-lived cloud credentials whenever the provider supports it
- [ ] `concurrency` is configured where duplicate runs would be harmful
- [ ] Branch and path filters match the intended trigger surface
- [ ] Allowed actions and reusable workflows are restricted at the repository or organization level
- [ ] `.github/workflows/**` and related automation code are protected by `CODEOWNERS`
- [ ] Dependency review is enabled for pull requests that change dependencies or workflows
- [ ] GitHub Actions workflow scanning is enabled in CodeQL or equivalent code scanning coverage
- [ ] OpenSSF Scorecards is enabled or otherwise tracked for workflow-level supply chain regressions
- [ ] Dependabot is configured for `github-actions` updates
- [ ] Artifact attestations, SBOM attestations, and immutable releases are used for publish/release flows
- [ ] Protected environments with required reviewers guard privileged deploys and publishers
