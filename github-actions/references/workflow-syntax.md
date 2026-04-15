# Workflow Syntax Reference

Workflows are YAML files in `.github/workflows/`. Use this file for syntax shape. Use [security-hardening.md](security-hardening.md) for trust boundaries, token strategy, runners, provenance, and supply chain controls.

## Basic Structure

```yaml
name: CI Pipeline

on: push

env:
  NODE_VERSION: '20'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
        with:
          persist-credentials: false
      - run: npm test
```

## `on` - Trigger Configuration

Single event:

```yaml
on: push
```

Multiple events:

```yaml
on: [push, pull_request]
```

Event with configuration:

```yaml
on:
  push:
    branches: [main, develop]
    paths:
      - 'src/**'
      - '!src/**/*.md'
  pull_request:
    types: [opened, synchronize, reopened]
```

## `env` - Environment Variables

Scope precedence is step > job > workflow:

```yaml
env:
  WORKFLOW_VAR: 'available everywhere'

jobs:
  example:
    env:
      JOB_VAR: 'available in this job'
    steps:
      - run: echo "$STEP_VAR"
        env:
          STEP_VAR: 'available in this step only'
```

## `jobs.<job_id>` - Job Configuration

### `runs-on`

GitHub-hosted runners:

```yaml
runs-on: ubuntu-latest
runs-on: ubuntu-24.04
runs-on: windows-latest
runs-on: macos-latest
runs-on: macos-14
```

Self-hosted runners:

```yaml
runs-on: self-hosted
runs-on: [self-hosted, linux, x64]
runs-on: [self-hosted, gpu]
```

> Caution: self-hosted runners are not a routine default. Do not use them for public repository pull requests. For runner isolation, runner groups, and just-in-time runners, see [security-hardening.md](security-hardening.md).

### `permissions`

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
```

### `environment`

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
```

### `defaults`

```yaml
jobs:
  build:
    defaults:
      run:
        shell: bash
        working-directory: ./app
```

### `timeout-minutes`

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30
```

## `jobs.<job_id>.steps`

### Using Actions

```yaml
steps:
  - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
    with:
      persist-credentials: false
  - uses: actions/setup-node@<full-commit-sha>  # vX.Y.Z
    with:
      node-version: '20'
      cache: 'npm'
```

### Running Commands

```yaml
steps:
  - run: npm ci
  - name: Run tests
    run: npm test
    working-directory: ./app
    shell: bash
    env:
      CI: true
```

### Multi-line Commands

```yaml
steps:
  - run: |
      echo "First command"
      echo "Second command"
      npm run build
```

### Step Outputs

Set output:

```yaml
steps:
  - id: get-version
    run: echo "version=$(cat VERSION)" >> "$GITHUB_OUTPUT"
```

Use output:

```yaml
- run: echo "Version is ${{ steps.get-version.outputs.version }}"
```

## `jobs.<job_id>.outputs`

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      artifact-id: ${{ steps.upload.outputs.artifact-id }}
    steps:
      - id: upload
        run: echo "artifact-id=123" >> "$GITHUB_OUTPUT"

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying artifact ${{ needs.build.outputs.artifact-id }}"
```

## `strategy.matrix`

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        node: [18, 20, 22]
        exclude:
          - os: windows-latest
            node: 18
        include:
          - os: ubuntu-latest
            node: 22
            experimental: true
      fail-fast: false
      max-parallel: 4
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-node@<full-commit-sha>  # vX.Y.Z
        with:
          node-version: ${{ matrix.node }}
```

## `concurrency`

Workflow level:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Job level:

```yaml
jobs:
  deploy:
    concurrency:
      group: production-deploy
      cancel-in-progress: false
```

## `services`

Prefer pinned digests for container and service images.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16@sha256:<image-digest>
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
```

## `container`

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: node:20@sha256:<image-digest>
      credentials:
        username: ${{ secrets.DOCKER_USER }}
        password: ${{ secrets.DOCKER_TOKEN }}
      env:
        NODE_ENV: production
      volumes:
        - /cache:/cache
```
