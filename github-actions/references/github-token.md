# GITHUB_TOKEN Reference

Use `GITHUB_TOKEN` by default. Scope it explicitly and keep it read-only unless a job has a clear need for additional privileges.

## Accessing the Token Safely

Any action can access the token through `github.token`, even if the workflow does not pass it explicitly. Scope permissions before using third-party actions.

Use the token as an environment variable for CLI or API tools:

```yaml
steps:
  - name: List issues
    run: gh issue list --repo "${{ github.repository }}"
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Default Permissions

Default permissions depend on repository, organization, and enterprise settings. A secure baseline is:

- set repository defaults to read-only for contents
- scope additional permissions explicitly in workflows
- prefer job-level permissions for privileged steps

Configure defaults in:
- Repository Settings > Actions > General > Workflow permissions
- Organization Settings > Actions > General > Workflow permissions

## Configuring Permissions

### Workflow-Level Permissions

Apply to all jobs:

```yaml
permissions:
  contents: read
  issues: write
```

### Job-Level Permissions

Prefer this when only one job needs write access:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read

  comment:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
```

### Disable All Permissions

```yaml
permissions: {}
```

If you specify any permission explicitly, all unspecified permissions become `none`.

## Available Permissions

| Permission | Example Use |
|------------|-------------|
| `actions` | Cancel or rerun workflow runs |
| `artifact-metadata` | Create linked-artifact storage records when a provenance flow needs them |
| `attestations` | Generate artifact or SBOM attestations |
| `checks` | Create or update check runs |
| `contents` | Read commits and files, or create releases when set to `write` |
| `deployments` | Create or update deployments |
| `discussions` | Read or update GitHub Discussions |
| `id-token` | Fetch an OIDC token for cloud auth |
| `issues` | Comment on or edit issues |
| `models` | Call GitHub Models inference APIs |
| `packages` | Publish or download GitHub Packages |
| `pages` | Request GitHub Pages builds |
| `pull-requests` | Label, comment on, or update pull requests |
| `security-events` | Upload SARIF or update code scanning alerts |
| `statuses` | Create commit statuses |

Each permission accepts `read`, `write`, or `none`. `write` includes `read`.

## Common Permission Patterns

### CI Build

```yaml
permissions:
  contents: read
```

### Pull Request Comment Bot

```yaml
permissions:
  contents: read
  pull-requests: write
```

### OIDC Deployment

```yaml
permissions:
  contents: read
  id-token: write
```

### Build Provenance

```yaml
permissions:
  contents: read
  attestations: write
  id-token: write
```

Add `artifact-metadata: write` only when the attestation flow requires linked-artifact metadata.

## Using with GitHub CLI

```yaml
steps:
  - name: Create issue
    run: |
      gh issue create \
        --repo "${{ github.repository }}" \
        --title "Automated issue" \
        --body "Created by workflow"
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Using with the REST API

```yaml
steps:
  - name: Create issue via API
    run: |
      curl --fail --request POST \
        --url "https://api.github.com/repos/${{ github.repository }}/issues" \
        --header "Authorization: Bearer $GH_TOKEN" \
        --header "Accept: application/vnd.github+json" \
        --data '{"title":"Automated issue","body":"Created by workflow"}'
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Token Limitations

1. `GITHUB_TOKEN` does not trigger additional workflows for most events. Exceptions are `workflow_dispatch` and `repository_dispatch`.
2. It is scoped to the current repository.
3. It does not bypass branch protections unless your policy explicitly allows that behavior.
4. It expires after the job completes.
5. On `pull_request_target`, GitHub grants a read/write repository token even when the event comes from a public fork. Treat that event as privileged.

## Escalation Path

### 1. Prefer `GITHUB_TOKEN`

Use it when the workflow only needs repository-local automation.

### 2. Prefer a GitHub App installation token when `GITHUB_TOKEN` is insufficient

Use this for:
- cross-repository automation
- permissions not available to `GITHUB_TOKEN`
- centrally managed automation identities
- intentionally triggering downstream workflows

Example:

```yaml
steps:
  - id: app-token
    uses: actions/create-github-app-token@<full-commit-sha>  # vX.Y.Z
    with:
      app-id: ${{ secrets.APP_ID }}
      private-key: ${{ secrets.APP_PRIVATE_KEY }}

  - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
    with:
      token: ${{ steps.app-token.outputs.token }}
```

### 3. Use a PAT only as a narrow fallback

Use a PAT only when a GitHub App is not viable, such as:
- a temporary migration
- a legacy integration you do not control
- a checkout path that cannot yet be moved to a GitHub App

If you must use a PAT:
- scope it minimally
- set an expiry
- store it as a secret
- rotate it regularly

## Anti-Patterns

Avoid these unless you can justify them in review:

```yaml
permissions: read-all
```

```yaml
permissions: write-all
```

Avoid making PAT-backed checkout or API access the documented default path.

## Security Best Practices

1. Set `permissions` explicitly for every workflow.
2. Keep read-only defaults at the workflow level and elevate per job only when necessary.
3. Never print tokens or secret values in logs.
4. Audit third-party actions because they can read `github.token`.
5. Use protected environments with required reviewers for deployment or publisher jobs.
6. Prefer OIDC over long-lived cloud secrets.
7. For trust-boundary questions such as `pull_request_target`, `workflow_run`, runners, provenance, and cache safety, defer to [security-hardening.md](security-hardening.md).
