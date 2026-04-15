# GitHub Action Setup

Release Please should run in a hardened workflow that separates release creation from publication. The default patterns below are grounded in the current `release-please-action` README, GitHub Actions token guidance, and npm trusted publishing docs.

## Pattern 1: Release Only with `GITHUB_TOKEN`

Use this when the workflow only needs to open or update release PRs, create tags, and create GitHub releases in the same repository.

```yaml
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

Use this pattern only when you do not need release PRs or releases to trigger additional workflows. GitHub prevents events created by `GITHUB_TOKEN` from fan-out into new workflow runs.

## Pattern 2: Release Plus Downstream Jobs with a GitHub App Token

Use this when release PRs, tags, or releases must trigger other workflows, or when the default token is not sufficient.

```yaml
name: release-and-publish

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
    outputs:
      release_created: ${{ steps.release.outputs.release_created }}
      tag_name: ${{ steps.release.outputs.tag_name }}
      version: ${{ steps.release.outputs.version }}
    steps:
      # create-github-app-token v2.2.2
      - uses: actions/create-github-app-token@fee1f7d63c2ff003460e3d139729b119787bc349
        id: app-token
        with:
          app-id: ${{ vars.RELEASE_APP_ID }}
          private-key: ${{ secrets.RELEASE_APP_PRIVATE_KEY }}

      # release-please-action v4.4.0
      - uses: googleapis/release-please-action@16a9c90856f42705d54a6fda1823352bdc62cf38
        id: release
        with:
          token: ${{ steps.app-token.outputs.token }}

  publish-npm:
    needs: release-please
    if: ${{ needs.release-please.outputs.release_created == 'true' }}
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      # actions/checkout v6.0.2
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd

      # actions/setup-node v6.3.0
      - uses: actions/setup-node@53b83947a5a98c8d113130e565377fae1a50d02f
        with:
          node-version: '22'
          registry-url: 'https://registry.npmjs.org'
          cache: npm

      - run: npm ci
      - run: npm test --if-present
      - run: npm publish --provenance --access public
```

Notes:

- Configure the npm package with a trusted publisher on npmjs.com before using the publish job.
- Trusted publishing only applies to `npm publish`; if `npm ci` needs private packages, use a separate read-only install credential.
- npm currently documents trusted publishing for GitHub-hosted runners only.

## Required Repository Settings

Release Please may need these repository settings:

1. **Settings -> Actions -> General -> Workflow permissions**
2. Enable **Allow GitHub Actions to create and approve pull requests** when `GITHUB_TOKEN` should open or update release PRs.

## Required Workflow Permissions

Current upstream baseline for `release-please-action`:

```yaml
permissions:
  contents: write
  issues: write
  pull-requests: write
```

Prefer job-level permissions so publish and deploy jobs can use narrower scopes.

## Action Inputs You Will Actually Use

| Input | Use |
|-------|-----|
| `token` | Authentication token for GitHub API access |
| `config-file` | Custom path to `release-please-config.json` |
| `manifest-file` | Custom path to `.release-please-manifest.json` |
| `target-branch` | Release branch override |
| `skip-github-release` | Open or update release PRs only |
| `skip-github-pull-request` | Tag and release only |
| `fork` | Fork-based PR creation for specific workflows |

For advanced release behavior, prefer manifest config over action inputs.

## Common Outputs

| Output | Meaning |
|--------|---------|
| `release_created` | `true` when the root package release was created |
| `tag_name` | Tag for the created release |
| `version` | Version without tag decoration |
| `major` / `minor` / `patch` | Parsed semver parts |
| `paths_released` | JSON array of released paths in a manifest repo |
| `prs_created` | `true` when release PRs were created or updated |

For package paths in monorepos, use `steps.release.outputs['path/to/pkg--release_created']`.

## Post-Release Asset Upload

Upload assets only after `release_created` is true:

```yaml
- name: Upload release asset
  if: ${{ steps.release.outputs.release_created == 'true' }}
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: gh release upload "${{ steps.release.outputs.tag_name }}" ./dist/app.tar.gz
```

## Post-Release Docker Publish

Keep Docker publication as a separate gated job with only the permissions it needs:

```yaml
docker:
  needs: release-please
  if: ${{ needs.release-please.outputs.release_created == 'true' }}
  runs-on: ubuntu-latest
  permissions:
    contents: read
    packages: write
  steps:
    # actions/checkout v6.0.2
    - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd

    # docker/login-action v4.1.0
    - uses: docker/login-action@4907a6ddec9925e35a0a9e82d7399ccc52663121
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    # docker/build-push-action v7.1.0
    - uses: docker/build-push-action@bcafcacb16a39f128d818304e6c9c0c18556b85f
      with:
        push: true
        tags: ghcr.io/${{ github.repository }}:${{ needs.release-please.outputs.version }}
```

## Major and Minor Tags for GitHub Actions

If you publish a GitHub Action, you may also need `v1` and `v1.2` tags:

```yaml
- name: Update major and minor tags
  if: ${{ steps.release.outputs.release_created == 'true' }}
  run: |
    git config user.name github-actions[bot]
    git config user.email 41898282+github-actions[bot]@users.noreply.github.com
    git tag -d "v${{ steps.release.outputs.major }}" || true
    git tag -d "v${{ steps.release.outputs.major }}.${{ steps.release.outputs.minor }}" || true
    git push origin ":v${{ steps.release.outputs.major }}" || true
    git push origin ":v${{ steps.release.outputs.major }}.${{ steps.release.outputs.minor }}" || true
    git tag -a "v${{ steps.release.outputs.major }}" -m "Release v${{ steps.release.outputs.major }}"
    git tag -a "v${{ steps.release.outputs.major }}.${{ steps.release.outputs.minor }}" -m "Release v${{ steps.release.outputs.major }}.${{ steps.release.outputs.minor }}"
    git push origin "v${{ steps.release.outputs.major }}"
    git push origin "v${{ steps.release.outputs.major }}.${{ steps.release.outputs.minor }}"
```

## Legacy Fallback: PAT

Use a fine-grained PAT only when:

- a GitHub App is not available
- `GITHUB_TOKEN` is insufficient
- you still need event fan-out or cross-repository behavior

PAT guidance:

1. Prefer fine-grained PATs scoped to a single repository.
2. Grant only the required permissions, typically `contents: write` and `pull-requests: write`.
3. Use short expiration dates and rotate them.
4. Treat classic `repo` PATs as last resort.

## Canonical References

- https://github.com/googleapis/release-please-action
- https://github.com/googleapis/release-please/blob/main/docs/manifest-releaser.md
- https://docs.github.com/en/actions/tutorials/authenticate-with-github_token
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- https://docs.npmjs.com/trusted-publishers
- https://docs.npmjs.com/generating-provenance-statements
- https://docs.npmjs.com/using-private-packages-in-a-ci-cd-workflow
