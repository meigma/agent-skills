# Using GitHub Actions Reference

For supply chain guidance, allowed-actions policy, and cache or artifact trust boundaries, see [security-hardening.md](security-hardening.md).

## Action Reference Syntax

```yaml
steps:
  - uses: OWNER/REPO@REF
  - uses: OWNER/REPO/PATH@REF
  - uses: ./.github/actions/my-action
  - uses: docker://IMAGE@sha256:DIGEST
```

## Always Pin to a Full Commit SHA

Pin every third-party action and every cross-repository reusable workflow to a full-length commit SHA.

Why:
- tags can move
- branches change constantly
- full SHAs are the only immutable workflow reference GitHub can enforce with policy
- the exact source revision is auditable

### Do This

```yaml
steps:
  - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
  - uses: actions/setup-node@<full-commit-sha>  # vX.Y.Z
```

### Do Not Do This

```yaml
steps:
  - uses: actions/checkout@v5
  - uses: actions/setup-node@main
```

### Resolving a SHA

Use the GitHub CLI to resolve a tag to the underlying commit:

```bash
gh api "repos/<owner>/<repo>/git/ref/tags/<tag>" --jq '.object.sha'
```

Keep the version comment on the same line so Dependabot can update both the SHA and the documentation comment:

```yaml
- uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
```

## Common Official Actions

### `actions/checkout`

Use minimal defaults and opt into extra behavior only when required.

```yaml
- uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
  with:
    persist-credentials: false
```

Enable additional options only when there is a clear need:

```yaml
- uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
  with:
    repository: owner/repo
    ref: main
    fetch-depth: 0
    fetch-tags: true
    submodules: recursive
    token: ${{ steps.app-token.outputs.token }}
```

Notes:
- `persist-credentials: false` is a good default for jobs that do not need authenticated git writes
- use a GitHub App token before considering a PAT
- `fetch-depth: 0` and `submodules` expand trust and network surface; do not enable them by default

### `actions/setup-node`

Use action-native package-manager caching instead of `node_modules` caches.

```yaml
- uses: actions/setup-node@<full-commit-sha>  # vX.Y.Z
  with:
    node-version: '20'
    cache: 'npm'
```

For privileged npm workflows where caching is not required, disable automatic package-manager caching:

```yaml
- uses: actions/setup-node@<full-commit-sha>  # vX.Y.Z
  with:
    node-version: '20'
    package-manager-cache: false
```

### `actions/cache`

Use `actions/cache` only when an action-specific cache is not available or you need explicit restore/save control.

Safe example:

```yaml
- uses: actions/cache@<full-commit-sha>  # vX.Y.Z
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

Do not document `node_modules` caching as a default.

### `actions/upload-artifact`

```yaml
- uses: actions/upload-artifact@<full-commit-sha>  # vX.Y.Z
  with:
    name: test-report
    path: |
      reports/
      !reports/**/*.map
    retention-days: 7
    if-no-files-found: error
```

Treat uploaded artifacts from untrusted workflows as data, not code.

### `actions/download-artifact`

```yaml
- uses: actions/download-artifact@<full-commit-sha>  # vX.Y.Z
  with:
    name: test-report
    path: ./artifacts
```

Do not execute scripts or binaries from untrusted artifacts in privileged jobs.

### `actions/github-script`

```yaml
- uses: actions/github-script@<full-commit-sha>  # vX.Y.Z
  with:
    script: |
      await github.rest.issues.createComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: context.issue.number,
        body: 'Hello from GitHub Script!'
      })
```

Use it for metadata operations. Avoid feeding untrusted input into shell commands inside the script.

## Action Inputs and Outputs

### Passing Inputs

```yaml
- uses: actions/setup-node@<full-commit-sha>  # vX.Y.Z
  with:
    node-version: '20'
    cache: 'npm'
```

### Using Outputs

```yaml
- id: node-setup
  uses: actions/setup-node@<full-commit-sha>  # vX.Y.Z
  with:
    node-version: '20'

- run: echo "Node version: ${{ steps.node-setup.outputs.node-version }}"
```

## Local Actions

Local actions are trusted to the same degree as the repository revision that checked them out.

```yaml
steps:
  - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
    with:
      persist-credentials: false
  - uses: ./.github/actions/my-action
    with:
      input1: value1
```

## Docker Actions

Pin Docker action references by digest.

```yaml
steps:
  - uses: docker://alpine@sha256:<image-digest>
    with:
      args: echo "Hello from Alpine"

  - uses: docker://ghcr.io/owner/action@sha256:<image-digest>
```

Notes:
- do not use unpinned `docker://image:tag` references
- Dependabot does not update `docker://` references automatically

## Versioning Best Practices

1. Pin to full SHAs in workflows and cross-repo reusable workflows.
2. Use Dependabot to keep actions and reusable workflows up to date:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

3. Review changelogs before updating actions.
4. Test updates in pull requests before merging.
5. Use repository or organization policy to restrict which actions and reusable workflows can run.

## Troubleshooting

### Action Not Found

```yaml
- uses: owner/repo@<full-commit-sha>
- uses: owner/repo/path@<full-commit-sha>
- uses: ./.github/actions/name
```

### Permission Denied

```yaml
permissions:
  contents: read
  packages: read
```

If the workflow still needs broader access, prefer a GitHub App token over a PAT.

### Private Action Repository

```yaml
steps:
  - id: app-token
    uses: actions/create-github-app-token@<full-commit-sha>  # vX.Y.Z
    with:
      app-id: ${{ secrets.APP_ID }}
      private-key: ${{ secrets.APP_PRIVATE_KEY }}

  - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
    with:
      repository: owner/private-action
      token: ${{ steps.app-token.outputs.token }}
      path: .github/actions/private-action

  - uses: ./.github/actions/private-action
```

Do not treat PAT-backed private action checkout as the default recommendation.
