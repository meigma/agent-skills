# Security Baseline

Use these rules as the default policy for any Release Please setup.

## Hard Requirements

1. Pin every third-party action by full commit SHA.
2. Use job-level `permissions` and grant only what that job requires.
3. Separate release creation from publish or deploy work.
4. Never expose write-capable GitHub tokens or registry credentials to untrusted pull request workflows.
5. Prefer `GITHUB_TOKEN` for self-contained release PR and release flows.
6. Prefer a GitHub App installation token over a PAT when `GITHUB_TOKEN` is not sufficient.
7. Prefer npm trusted publishing with OIDC over long-lived npm write tokens.
8. Enable release immutability when repository policy allows it.

## Token Hierarchy

Use tokens in this order:

1. `GITHUB_TOKEN` for release PRs, tags, and GitHub releases in the same repository
2. GitHub App installation token for downstream workflow triggering or additional repository permissions
3. Fine-grained PAT only as a fallback

For npm:

1. Trusted publishing with OIDC for `npm publish`
2. Read-only granular tokens for installing private dependencies when needed
3. Granular write tokens with bypass 2FA only when trusted publishing is not available

## Release Workflow Boundaries

Good default split:

- release workflow: opens or updates release PRs, creates tags, creates GitHub releases
- publish workflow or publish job: runs only after `release_created == 'true'`
- deploy workflow: depends on published artifacts, not on open PR state

This separation limits blast radius and keeps high-value credentials out of the release calculation step.

## GitHub Actions Guidance

Release job baseline:

```yaml
permissions:
  contents: write
  issues: write
  pull-requests: write
```

npm publish job baseline:

```yaml
permissions:
  contents: read
  id-token: write
```

Docker publish job baseline:

```yaml
permissions:
  contents: read
  packages: write
```

Do not grant write scopes to jobs that only build, test, or inspect artifacts.

## npm Trusted Publishing Notes

- Configure a trusted publisher on npmjs.com for the exact GitHub repository and workflow file.
- Use GitHub-hosted runners.
- Trusted publishing applies to `npm publish`, not to dependency installation.
- For public packages in public repositories, trusted publishing automatically gives you provenance generation; `--provenance` is still fine as an explicit signal in examples.

## Release Integrity

If you create draft GitHub releases, pair them with `force-tag-creation` so Release Please can still locate the previous release correctly.

If your repository supports it, enable GitHub release immutability so published releases cannot be changed later.

## What to Avoid

- mutable `@vN` action refs in release or publish workflows
- classic broad-scope PATs for routine release automation
- publish jobs that run inside untrusted `pull_request` workflows
- reusing the same credential for release management and package publication
- treating `autorelease: published` as if Release Please adds it automatically

## Canonical References

- https://docs.github.com/en/actions/tutorials/authenticate-with-github_token
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/preventing-changes-to-your-releases
- https://docs.npmjs.com/trusted-publishers
- https://docs.npmjs.com/using-private-packages-in-a-ci-cd-workflow
- https://docs.npmjs.com/generating-provenance-statements
