# Troubleshooting

Use this page to debug Release Please behavior without normalizing insecure release patterns.

## CLI Debugging

For local investigation, a one-off CLI invocation is safer than a permanent global install:

```bash
npx release-please@17.5.2 release-pr \
  --token="$GITHUB_TOKEN" \
  --repo-url=owner/repo \
  --dry-run \
  --debug
```

For more verbose traces:

```bash
npx release-please@17.5.2 release-pr \
  --token="$GITHUB_TOKEN" \
  --repo-url=owner/repo \
  --dry-run \
  --trace
```

## Release PR Not Created

Check these first:

1. The workflow runs on the correct branch.
2. Commits contain releasable Conventional Commit types such as `feat:` or `fix:`.
3. A release PR is not already open with `autorelease: pending`.
4. The workflow has `contents: write`, `issues: write`, and `pull-requests: write`.

List pending release PRs:

```bash
gh pr list --label "autorelease: pending"
```

## Release PR Opens but Version Is Wrong

Common causes:

- commit messages do not follow the expected format
- `.release-please-manifest.json` is out of sync
- `bootstrap-sha` or `last-release-sha` are set incorrectly
- `<1.0.0` behavior was misunderstood and defaults were never overridden

Verify recent commits:

```bash
git log --oneline -10
```

For `<1.0.0`, remember:

- breaking changes are major by default
- features are minor by default
- patch-only feature behavior requires `bump-patch-for-minor-pre-major: true`

## Breaking Change Did Not Produce a Major Release

Check for one of these:

```text
feat!: replace the public API
```

or

```text
feat(api): replace the public API

BREAKING CHANGE: Existing clients must migrate to v2.
```

Then confirm you did not explicitly opt into `bump-minor-pre-major` for versions below `1.0.0`.

## `403` or `Resource not accessible by integration`

Most commonly:

1. Missing workflow permissions.
2. Repository settings do not allow Actions to create PRs.
3. The token type is wrong for the job.

Baseline release permissions:

```yaml
permissions:
  contents: write
  issues: write
  pull-requests: write
```

Escalation order:

1. `GITHUB_TOKEN` for self-contained release PR and release operations
2. GitHub App installation token for extra permissions or event fan-out
3. Fine-grained PAT only as a fallback

## Release Events Did Not Trigger Other Workflows

This is expected when Release Please uses `GITHUB_TOKEN`. GitHub suppresses workflow fan-out from events created by that token to avoid recursion.

If you need downstream workflows:

1. Switch the release job to a GitHub App installation token.
2. Keep release creation and publish jobs separate.
3. Gate downstream jobs on `release_created`.

Do not treat PATs as the default answer here unless a GitHub App is not available.

## npm Trusted Publishing Failed

Check these conditions:

1. The publish job runs on a GitHub-hosted runner.
2. The workflow has `id-token: write`.
3. The trusted publisher entry on npm matches the repository and workflow filename exactly.
4. The npm CLI and Node version meet npm's current trusted publishing requirements.

Minimal publish-job permissions:

```yaml
permissions:
  contents: read
  id-token: write
```

If `npm ci` fails on private dependencies, remember that trusted publishing only covers `npm publish`. Use a separate read-only install credential for dependency installation.

## Draft Releases Keep Reusing Old History

GitHub draft releases delay tag creation by default. If Release Please cannot find the previous tag after a draft release, enable:

```json
{
  "draft": true,
  "force-tag-creation": true
}
```

## Manifest File Out of Sync

Set the manifest entry to the latest released version:

```json
{
  ".": "2.3.4"
}
```

Then rerun a dry-run release PR calculation.

## Monorepo Package Not Detected

Check:

1. The package path is relative to the repo root.
2. The path matches the real directory exactly.
3. The commit changed files inside that path.
4. `exclude-paths` did not filter out the changes.

Correct path style:

```json
{
  "packages": {
    "packages/core": {}
  }
}
```

Incorrect path styles:

```json
{
  "packages": {
    "packages/core/": {},
    "./packages/core": {}
  }
}
```

## Mutable Action Refs in Release Pipelines

If your workflow still uses `@v4`, `@v5`, or other mutable tags in release or publish jobs, replace them with full commit SHAs. This is one of the easiest supply-chain improvements you can make.

## Canonical References

- https://github.com/googleapis/release-please
- https://github.com/googleapis/release-please-action
- https://docs.github.com/en/actions/tutorials/authenticate-with-github_token
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- https://docs.npmjs.com/trusted-publishers
- https://docs.npmjs.com/using-private-packages-in-a-ci-cd-workflow
- https://docs.npmjs.com/generating-provenance-statements
