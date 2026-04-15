# Events and Triggers Reference

Choose the least-privileged trigger that satisfies the workflow. For trust boundaries, privileged follow-up patterns, and fork safety, see [security-hardening.md](security-hardening.md).

## Common Webhook Events

### `push`

Triggered on commits pushed to a branch or tag.

```yaml
on:
  push:
    branches:
      - main
      - 'releases/**'
    branches-ignore:
      - 'feature/**'
    tags:
      - 'v*'
    paths:
      - 'src/**'
      - '!src/**/*.test.js'
```

Context variables:
- `GITHUB_SHA`: commit that triggered the workflow
- `GITHUB_REF`: full ref such as `refs/heads/main`

### `pull_request`

Triggered on pull request activity against the base repository.

Use this as the default trigger for build, test, lint, and static analysis jobs that execute contributor code.

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
    branches:
      - main
    paths:
      - 'src/**'
```

Activity types:
- `opened`
- `synchronize`
- `reopened`
- `closed` (check `github.event.pull_request.merged` for merge status)
- `ready_for_review`
- `converted_to_draft`
- `labeled` / `unlabeled`
- `assigned` / `unassigned`
- `review_requested` / `review_request_removed`

Default types when `types` is omitted: `opened`, `synchronize`, `reopened`

Context variables:
- `GITHUB_SHA`: last merge commit on the PR merge branch
- `GITHUB_REF`: PR merge branch such as `refs/pull/<number>/merge`
- `github.event.pull_request.head.sha`: actual pull request head commit

Fork note:
- public repositories can require approval before some fork-based workflow runs start
- `pull_request_target` bypasses that approval model because it runs in the base branch context

### `pull_request_target`

This is a privileged trigger. It runs using the base branch workflow definition and receives a read/write repository token, even for public forks.

Use it only for metadata operations that do not check out or execute untrusted pull request code.

Safe uses:
- add labels
- post comments
- route to a trusted reusable workflow
- dispatch a privileged follow-up that never checks out PR code

Safe example:

```yaml
name: PR Metadata

on:
  pull_request_target:
    types: [opened, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  comment:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@<full-commit-sha>  # vX.Y.Z
        with:
          script: |
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: 'Thanks for the pull request. A maintainer will review CI results from the unprivileged workflow.'
            })
```

Explicit anti-pattern:

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

Do not:
- check out `github.event.pull_request.head.sha`
- run scripts from the pull request
- restore caches from untrusted pull request workloads
- grant secrets or cloud credentials to the job

### `workflow_dispatch`

Manual trigger with typed inputs.

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        type: choice
        options:
          - staging
          - production
      dry-run:
        description: 'Skip mutating deployment steps'
        required: false
        type: boolean
        default: false
      version:
        description: 'Version to deploy'
        required: false
        type: string
```

Access inputs:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to ${{ inputs.environment }}"
      - if: ${{ inputs.dry-run }}
        run: echo "Dry run - no changes made"
```

### `schedule`

Cron-based scheduling in UTC.

```yaml
on:
  schedule:
    - cron: '0 0 * * *'
    - cron: '30 5 * * 1-5'
```

Notes:
- minimum interval is 5 minutes
- scheduled workflows may be delayed during high load
- public repository schedules are disabled after 60 days of repository inactivity
- scheduled workflows run only on the default branch

### `workflow_call`

Makes the workflow reusable by other workflows. See [reusable-workflows.md](reusable-workflows.md).

```yaml
on:
  workflow_call:
    inputs:
      config-path:
        required: true
        type: string
    secrets:
      token:
        required: true
    outputs:
      result:
        description: 'Build result'
        value: ${{ jobs.build.outputs.result }}
```

### `workflow_run`

Triggered when another workflow run is requested or completes.

This is a privileged follow-up trigger. Use it for separation of duties, not for a second chance to run untrusted code with more power.

```yaml
on:
  workflow_run:
    workflows: ["Pull Request CI"]
    types: [completed]
```

Safe split-workflow example:

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
      - uses: actions/github-script@<full-commit-sha>  # vX.Y.Z
        with:
          script: |
            const pr = context.payload.workflow_run.pull_requests[0];
            if (!pr) {
              return;
            }
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: pr.number,
              body: 'CI passed. Review uploaded artifacts as data only before taking privileged action.'
            });
```

Rules:
- do not check out pull request head commits in the privileged workflow
- do not execute scripts from uploaded artifacts
- treat outputs and artifacts from the triggering workflow as untrusted data
- prefer machine-readable reports over executable payloads

### `release`

Triggered on release activity.

```yaml
on:
  release:
    types: [published, created, released]
```

Activity types: `published`, `unpublished`, `created`, `edited`, `deleted`, `prereleased`, `released`

### `issue_comment`

Triggered on issue or pull request comments.

```yaml
on:
  issue_comment:
    types: [created]
```

Filter to pull request comments only:

```yaml
jobs:
  pr-comment:
    if: github.event.issue.pull_request
    runs-on: ubuntu-latest
```

Treat comment bodies as untrusted input.

### `repository_dispatch`

External trigger via API.

```yaml
on:
  repository_dispatch:
    types: [deploy, custom-event]
```

Trigger via API:

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/OWNER/REPO/dispatches \
  -d '{"event_type":"deploy","client_payload":{"environment":"prod"}}'
```

Access payload:

```yaml
steps:
  - run: echo "Deploying to ${{ github.event.client_payload.environment }}"
```

## Less Common Events

| Event | Description |
|-------|-------------|
| `create` | Branch or tag created |
| `delete` | Branch or tag deleted |
| `fork` | Repository forked |
| `issues` | Issue activity |
| `label` | Label created, edited, deleted |
| `milestone` | Milestone activity |
| `page_build` | GitHub Pages build |
| `project` | Project board activity |
| `public` | Repository made public |
| `status` | Commit status updated |
| `watch` | Repository starred |
| `discussion` | Discussion activity |
| `discussion_comment` | Discussion comment activity |

## Multiple Events

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * 0'
```

## Filter Patterns

Patterns support `*`, `**`, `+`, `?`, `!`:

```yaml
on:
  push:
    branches:
      - main
      - 'releases/**'
      - '!releases/**-alpha'
    paths:
      - 'src/**'
      - '**.js'
      - '!**/*.test.js'
```
