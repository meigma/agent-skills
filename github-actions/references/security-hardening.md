# Security Hardening Reference

Use this file as the canonical reference for trust boundaries, privileged triggers, tokens, runners, provenance, and supply chain controls in GitHub Actions.

## Security Model

- Treat workflow files as privileged code.
- Treat repository contents from pull requests, issue bodies, labels, titles, branch names, artifact contents, and reusable workflow inputs as potentially attacker-controlled unless proven otherwise.
- Prefer the simplest trust model that works:
  - untrusted build/test on `pull_request`
  - privileged metadata changes on `pull_request_target` only when no untrusted code is checked out
  - privileged follow-up on `workflow_run` only when artifacts are handled as data, not executed code

## Trusted vs Untrusted Triggers

### Default choice for contributor code: `pull_request`

Use `pull_request` for build, test, lint, and static analysis jobs that execute repository code from a pull request.

Safe defaults:
- `permissions: contents: read`
- no secrets
- no cloud credentials
- no write tokens
- no self-hosted runners for public repositories

### Privileged trigger: `pull_request_target`

`pull_request_target` runs in the context of the base branch and receives a read/write repository token, even for public forks. Use it only for metadata operations that do not check out or execute untrusted code.

Good uses:
- add labels
- post comments
- triage based on event metadata
- dispatch a trusted follow-up workflow

Do not:
- check out `${{ github.event.pull_request.head.sha }}`
- run build scripts from the pull request
- restore caches created by untrusted workloads
- consume arbitrary artifacts as executable input

### Privileged trigger: `workflow_run`

`workflow_run` is useful for privilege separation, but it is still a privileged trigger. Treat artifacts and outputs from the triggering workflow as untrusted unless they were produced entirely from trusted code.

Good uses:
- post a status comment after reading a machine-readable report as data
- gate deployment after a trusted build workflow
- verify attestations or release metadata

Do not:
- check out the pull request head from the triggering run
- execute scripts contained in artifacts uploaded by untrusted workflows
- restore caches from untrusted workflows into privileged jobs

### Fork approvals

For public repositories, GitHub can require approval before workflows from external contributors run. This reduces runner abuse, but it does not make privileged triggers safe:

- `pull_request` may require approval depending on repository settings
- `pull_request_target` bypasses those approval settings because it runs in the base branch context
- self-hosted runners remain at risk even when fork approvals are enabled

## Privileged Workflow Separation

Separate untrusted execution from privileged operations.

### Safe split-workflow pattern

Workflow A executes untrusted code with read-only permissions:

```yaml
name: Pull Request CI

on:
  pull_request:

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
        with:
          persist-credentials: false
      - run: ./ci.sh
      - uses: actions/upload-artifact@<full-commit-sha>  # vX.Y.Z
        with:
          name: pr-report
          path: report.json
```

Workflow B performs a privileged follow-up without checking out pull request code:

```yaml
name: Pull Request Follow Up

on:
  workflow_run:
    workflows: ["Pull Request CI"]
    types: [completed]

permissions:
  contents: read
  pull-requests: write

jobs:
  comment:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      - name: Download artifact metadata only
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          RUN_ID: ${{ github.event.workflow_run.id }}
        run: gh api repos/${{ github.repository }}/actions/runs/$RUN_ID/artifacts
      - name: Post trusted summary
        uses: actions/github-script@<full-commit-sha>  # vX.Y.Z
        with:
          script: |
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.payload.workflow_run.pull_requests[0].number,
              body: 'CI completed. Review report.json as data before taking further action.'
            })
```

### Explicit anti-pattern

This is unsafe because it runs attacker-controlled code with a privileged token:

```yaml
name: Unsafe PR Build

on:
  pull_request_target:
    types: [opened, synchronize]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: npm ci && npm test
```

## Token Strategy

Choose the least-privileged token that satisfies the use case.

1. `GITHUB_TOKEN`
   - default choice inside a workflow
   - scope permissions explicitly with `permissions`
   - use read-only defaults and elevate per job only when needed

2. GitHub App installation token
   - preferred escalation path when `GITHUB_TOKEN` is insufficient
   - use for cross-repository automation, special repository permissions, or workflow-triggering actions that should remain centrally managed
   - mint the token inside the workflow and treat the private key as the protected secret

3. Personal access token
   - last resort for narrow legacy cases
   - use only when a GitHub App is not viable
   - scope minimally and rotate aggressively

Never:
- rely on implicit default permissions
- use `write-all` as a shortcut
- print tokens or pass them through untrusted commands
- give an untrusted job a write-capable token

## Action and Workflow Supply Chain Controls

### Pinning and source review

- Pin every third-party action to a full-length commit SHA.
- Pin every cross-repository reusable workflow to a full-length commit SHA.
- Audit the source of new actions before adoption.
- A Marketplace verified creator badge is a useful signal, not a security boundary.

### Repository and organization enforcement

Use GitHub Actions settings to:
- require full-length commit SHAs for actions
- allow only GitHub-authored actions, verified creators, or explicit allowlists
- block risky or unneeded actions and reusable workflows
- prevent GitHub Actions from creating or approving pull requests without oversight

### Workflow change control

- Protect `.github/workflows/**`, `.github/actions/**`, and release automation files with `CODEOWNERS`.
- Require review from the team that owns CI/CD and release security.

## Dependency and Workflow Review Controls

Enable the controls that catch supply chain regressions before merge:

- Dependabot for `github-actions` updates
- dependency review on pull requests
- CodeQL or equivalent code scanning with GitHub Actions workflow scanning enabled
- OpenSSF Scorecards or equivalent workflow-policy scanning

Treat workflow changes as security-sensitive even if application code is untouched.

## Release Provenance and Verification

Publishing workflows should emit provenance that downstream consumers can verify.

### Build provenance attestation

```yaml
permissions:
  contents: read
  attestations: write
  id-token: write
```

```yaml
- name: Generate artifact attestation
  uses: actions/attest-build-provenance@<full-commit-sha>  # v3
  with:
    subject-path: dist/my-artifact.tar.gz
```

### SBOM attestation

```yaml
permissions:
  contents: read
  attestations: write
  id-token: write
```

```yaml
- name: Generate SBOM attestation
  uses: actions/attest-sbom@<full-commit-sha>  # v2
  with:
    subject-path: dist/my-artifact.tar.gz
    sbom-path: sbom.spdx.json
```

### Linked artifacts metadata

Add `artifact-metadata: write` only when the attestation flow needs linked-artifact storage metadata, such as registry-pushed image provenance with linked artifact records.

### Verification

Use the GitHub CLI to verify build provenance and SBOM attestations:

```bash
gh attestation verify dist/my-artifact.tar.gz -R OWNER/REPO

gh attestation verify dist/my-artifact.tar.gz \
  -R OWNER/REPO \
  --predicate-type https://spdx.dev/Document/v2.3
```

### Immutable releases

For published artifacts:
- use immutable releases where available
- attach release attestations or provenance to release assets
- document how consumers can verify what was built and published

## Runner Hardening

### Default choice: GitHub-hosted runners

Prefer GitHub-hosted runners for public repositories and for any workflow that executes untrusted code.

### Self-hosted runners

Self-hosted runners are high risk because untrusted workflows can compromise the host environment.

Rules:
- do not use self-hosted runners for public repository pull requests
- isolate sensitive workloads into dedicated runner groups
- keep network reachability and host secrets to a minimum
- use just-in-time or ephemeral runners where possible
- do not assume one-job-per-runner if the underlying host is reused

## Cache and Artifact Trust Boundaries

- Do not share privileged caches with untrusted jobs.
- Do not restore caches from untrusted workflows into privileged follow-up jobs.
- Treat artifacts from untrusted workflows as data, not executable code.
- Avoid caching `node_modules`; prefer package-manager caches or action-native caches.
- For privileged npm workflows where caching is unnecessary, disable automatic setup-node package-manager caching.

Safe example for a privileged npm workflow:

```yaml
- uses: actions/setup-node@<full-commit-sha>  # vX.Y.Z
  with:
    node-version: '20'
    package-manager-cache: false
```

## Quick Decision Guide

- Need to run contributor code? Use `pull_request`.
- Need to label or comment on a pull request? Use `pull_request_target` without checkout.
- Need a privileged follow-up after untrusted CI? Use `workflow_run` without checkout and treat artifacts as untrusted data.
- Need cloud auth? Use OIDC before secrets.
- Need more than `GITHUB_TOKEN` can do? Use a GitHub App before considering a PAT.
- Need to publish artifacts? Add provenance, SBOM attestations, and immutable release practices.
