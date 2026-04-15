# Reusable Workflows Reference

Reusable workflows reduce duplication and centralize CI/CD policy, but they also create cross-repository trust boundaries. Pin cross-repository calls to full SHAs and keep permissions and secrets explicit. For the security model behind these rules, see [security-hardening.md](security-hardening.md).

## Creating a Reusable Workflow

File: `.github/workflows/reusable-build.yml`

```yaml
name: Reusable Build Workflow

on:
  workflow_call:
    inputs:
      node-version:
        description: 'Node.js version'
        required: false
        type: string
        default: '20'
      working-directory:
        description: 'Working directory'
        required: false
        type: string
        default: '.'
    secrets:
      npm-token:
        description: 'Registry authentication token'
        required: false
    outputs:
      artifact-name:
        description: 'Name of the uploaded artifact'
        value: ${{ jobs.build.outputs.artifact-name }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      artifact-name: ${{ steps.meta.outputs.artifact-name }}
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
        with:
          persist-credentials: false
      - uses: actions/setup-node@<full-commit-sha>  # vX.Y.Z
        with:
          node-version: ${{ inputs.node-version }}
          cache: 'npm'
      - run: npm ci
        env:
          NODE_AUTH_TOKEN: ${{ secrets.npm-token }}
      - run: npm run build
      - id: meta
        run: echo "artifact-name=build-${GITHUB_SHA}" >> "$GITHUB_OUTPUT"
      - uses: actions/upload-artifact@<full-commit-sha>  # vX.Y.Z
        with:
          name: ${{ steps.meta.outputs.artifact-name }}
          path: ${{ inputs.working-directory }}/dist
```

## Input Types

```yaml
on:
  workflow_call:
    inputs:
      string-input:
        type: string
        required: true
      boolean-input:
        type: boolean
        default: false
      number-input:
        type: number
        default: 10
```

Available types: `string`, `boolean`, `number`

## Secrets

### Prefer Named Secrets

Pass only the specific secrets the callee needs:

```yaml
jobs:
  build:
    uses: ./.github/workflows/reusable-build.yml
    secrets:
      npm-token: ${{ secrets.NPM_TOKEN }}
```

### `secrets: inherit` is the exception

Use `secrets: inherit` only when:
- caller and callee are in the same trust boundary
- the callee is intentionally designed to receive every caller secret
- the broader secret surface is reviewed and accepted

Warning example:

```yaml
jobs:
  shared-platform-workflow:
    uses: org/platform/.github/workflows/platform.yml@<full-commit-sha>  # vX.Y.Z
    secrets: inherit
```

Do not use `secrets: inherit` as the default recommendation for shared or multi-tenant reusable workflows.

## Outputs

Map step outputs to job outputs, then expose them at `workflow_call.outputs`:

```yaml
on:
  workflow_call:
    outputs:
      version:
        description: 'Version that was built'
        value: ${{ jobs.build.outputs.version }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - id: version
        run: echo "version=1.2.3" >> "$GITHUB_OUTPUT"
```

## Calling a Reusable Workflow

### Same Repository

When you omit `OWNER/REPO@REF`, GitHub uses the workflow from the same commit as the caller.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  build:
    uses: ./.github/workflows/reusable-build.yml
    with:
      node-version: '20'
    secrets:
      npm-token: ${{ secrets.NPM_TOKEN }}
```

### Another Repository

Cross-repository calls must be pinned to a full commit SHA.

```yaml
jobs:
  build:
    permissions:
      contents: read
    uses: owner/repo/.github/workflows/reusable-build.yml@<full-commit-sha>  # vX.Y.Z
    with:
      node-version: '20'
```

Do not document branch references such as `@main` as the default cross-repository pattern.

## Using Outputs

```yaml
jobs:
  build:
    uses: ./.github/workflows/reusable-build.yml

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying ${{ needs.build.outputs.artifact-name }}"
```

## Using a Matrix Strategy with a Reusable Workflow

Caller jobs can use `strategy.matrix` when invoking a reusable workflow.

```yaml
jobs:
  deploy:
    strategy:
      matrix:
        environment: [staging, production]
    permissions:
      contents: read
      id-token: write
    uses: owner/repo/.github/workflows/deploy.yml@<full-commit-sha>  # vX.Y.Z
    with:
      environment: ${{ matrix.environment }}
```

## Permissions in Reusable Workflows

- the caller defines the effective permissions
- nested reusable workflows can maintain or reduce permissions, never elevate them
- keep privileged permissions at the narrowest caller job that needs them

Example:

```yaml
jobs:
  deploy:
    permissions:
      contents: read
      id-token: write
    uses: ./.github/workflows/deploy.yml
```

## Nesting Reusable Workflows

Reusable workflows can be nested up to 10 levels total, counting the top-level caller workflow.

```yaml
jobs:
  level1:
    uses: ./.github/workflows/level2.yml
```

Rules:
- all workflows in the chain must be accessible to the original caller
- permissions can only be maintained or reduced through the chain
- secrets only flow to directly called workflows unless they are passed onward explicitly

## Environment Limitations

Environment secrets cannot be passed from the caller through `workflow_call`. If the called workflow sets `environment` at the job level, that job uses the environment secrets defined in the called repository or environment context.

```yaml
jobs:
  deploy:
    uses: ./.github/workflows/deploy.yml
    with:
      environment: production
```

In the reusable workflow:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
```

## Practical Rules

1. Prefer same-repository reusable workflows for tightly coupled CI logic.
2. Use cross-repository reusable workflows for centrally governed automation, but pin them to full SHAs.
3. Pass named secrets whenever possible.
4. Keep permissions explicit at the caller job.
5. Treat reusable workflows as privileged supply chain dependencies and review them accordingly.
