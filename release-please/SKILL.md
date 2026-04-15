---
name: configuring-release-please
description: Configures automated releases using release-please. Use when setting up release-please, configuring release-please-config.json, creating .release-please-manifest.json, setting up GitHub Actions for automated releases, implementing Conventional Commits, configuring monorepo releases, or troubleshooting release automation.
---

# Configuring Release Please

Release Please automates release pull requests, version bumps, tags, and GitHub releases from Conventional Commits. It does not publish to package registries by itself; publishing should be a separate, gated workflow that runs only after a release is created.

## Recommended Operating Model

1. Use manifest configuration files as the source of truth: `release-please-config.json` and `.release-please-manifest.json`.
2. Use `GITHUB_TOKEN` only for self-contained release PR and GitHub release flows.
3. Use a GitHub App installation token when release actions must trigger downstream workflows or need permissions beyond the default token.
4. Pin every third-party action by full commit SHA and keep permissions at the job level with the minimum required scope.
5. Keep release creation separate from publish or deploy jobs, and gate downstream jobs on `release_created`.
6. Prefer npm trusted publishing with OIDC over long-lived write tokens.
7. Treat `autorelease: published` as a downstream convention, not an automatic Release Please label.
8. Squash merges are recommended for cleaner changelogs, but Release Please works with merge commits too.

## Quick Reference

| Topic | Details |
|-------|---------|
| Configuration Files | [configuration.md](configuration.md) |
| GitHub Action Setup | [github-action.md](github-action.md) |
| Security Baseline | [security.md](security.md) |
| Conventional Commits | [conventional-commits.md](conventional-commits.md) |
| Monorepo Setup | [monorepo.md](monorepo.md) |
| Troubleshooting | [troubleshooting.md](troubleshooting.md) |

## Essential Files

### release-please-config.json

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "release-type": "node",
  "packages": {
    ".": {}
  }
}
```

### .release-please-manifest.json

```json
{
  ".": "1.0.0"
}
```

## Hardened Release Workflow

Use this pattern when Release Please only needs to open or update release PRs, create tags, and create GitHub releases in the same repository.

```yaml
# .github/workflows/release-please.yml
name: release-please

on:
  push:
    branches:
      - main

jobs:
  release-please:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
    steps:
      # release-please-action v4.4.0
      - uses: googleapis/release-please-action@16a9c90856f42705d54a6fda1823352bdc62cf38
        id: release
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
```

If releases or release PRs must trigger other workflows, switch to the GitHub App token pattern in [github-action.md](github-action.md).

## Common Built-In Release Types

Release Please supports many built-in strategies. Common ones include:

| Type | Typical Use |
|------|-------------|
| `node` | Node.js packages |
| `python` | Python packages |
| `go` | Go modules |
| `rust` | Rust crates |
| `java` / `maven` | Maven projects |
| `ruby` | Ruby gems |
| `helm` | Helm charts |
| `simple` | Generic repositories with explicit version files |

For the full current list, use the upstream README referenced below.

## Release Labels

| Label | Meaning |
|-------|---------|
| `autorelease: pending` | Release PR is open and awaiting merge |
| `autorelease: tagged` | Release PR was merged and tagged |
| `autorelease: snapshot` | Snapshot workflow state for supported strategies |
| `autorelease: published` | Optional downstream convention for publish tooling; Release Please does not add it automatically |

## Common Patterns

### Single Package Repository

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "release-type": "node",
  "packages": {
    ".": {}
  }
}
```

### Custom Changelog Sections

```json
{
  "release-type": "node",
  "packages": {
    ".": {}
  },
  "changelog-sections": [
    {"type": "feat", "section": "Features"},
    {"type": "fix", "section": "Bug Fixes"},
    {"type": "perf", "section": "Performance"},
    {"type": "revert", "section": "Reverts"},
    {"type": "docs", "section": "Documentation", "hidden": true},
    {"type": "chore", "section": "Maintenance", "hidden": true}
  ]
}
```

### Tag Format

```json
{
  "release-type": "go",
  "include-v-in-tag": true,
  "packages": {
    ".": {}
  }
}
```

### Prerelease Versions

```json
{
  "release-type": "node",
  "versioning": "prerelease",
  "prerelease": true,
  "prerelease-type": "beta",
  "packages": {
    ".": {}
  }
}
```

## Version Bump Rules

Default behavior:

| Commit Type | Version Impact |
|-------------|----------------|
| `fix:` | Patch |
| `feat:` | Minor |
| `feat!:` or `BREAKING CHANGE:` | Major |

For versions below `1.0.0`, Release Please still uses the default semver strategy unless you explicitly opt into `bump-minor-pre-major` or `bump-patch-for-minor-pre-major`.

## Manual Version Override

Prefer a `Release-As:` footer in the commit body over config-level `release-as` overrides:

```text
chore: cut the next stable release

Release-As: 2.0.0
```

## Extra Files

Use `extra-files` when a strategy needs to update additional version-bearing files:

```json
{
  "extra-files": [
    "version.txt",
    {
      "type": "json",
      "path": "package.json",
      "jsonpath": "$.version"
    },
    {
      "type": "yaml",
      "path": "chart/Chart.yaml",
      "jsonpath": "$.appVersion"
    }
  ]
}
```

For arbitrary files, use the generic inline annotation format:

```go
// x-release-please-version
const Version = "1.0.0"
```

## Canonical References

- https://github.com/googleapis/release-please
- https://github.com/googleapis/release-please/blob/main/docs/manifest-releaser.md
- https://github.com/googleapis/release-please/blob/main/docs/customizing.md
- https://github.com/googleapis/release-please-action
- https://docs.github.com/en/actions/tutorials/authenticate-with-github_token
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- https://docs.npmjs.com/trusted-publishers
