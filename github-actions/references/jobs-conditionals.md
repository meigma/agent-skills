# Jobs, Dependencies, and Conditionals Reference

## Job Dependencies

### Basic Dependency

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm run build

  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: npm test
```

### Multiple Dependencies

```yaml
jobs:
  build:
    runs-on: ubuntu-latest

  lint:
    runs-on: ubuntu-latest

  test:
    needs: [build, lint]   # Waits for both
    runs-on: ubuntu-latest
```

### Dependency Chain

```yaml
jobs:
  build:
    runs-on: ubuntu-latest

  test:
    needs: build
    runs-on: ubuntu-latest

  deploy:
    needs: test
    runs-on: ubuntu-latest
```

### Accessing Outputs from Dependencies

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - id: version
        run: echo "version=1.2.3" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying version ${{ needs.build.outputs.version }}"
```

## Conditionals (`if`)

### Job Conditionals

```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
```

### Step Conditionals

```yaml
steps:
  - name: Deploy to production
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    run: ./deploy.sh prod

  - name: Deploy to staging
    if: github.event_name == 'pull_request'
    run: ./deploy.sh staging
```

### Expression Syntax

The `${{ }}` wrapper is optional for `if` but required when expression starts with `!`:
```yaml
if: github.ref == 'refs/heads/main'           # Works
if: ${{ github.ref == 'refs/heads/main' }}    # Also works
if: ${{ !cancelled() }}                        # Required (starts with !)
```

## Status Check Functions

### `success()`

True if all previous steps succeeded (default behavior):
```yaml
steps:
  - run: exit 1
  - run: echo "This won't run"
  - if: success()
    run: echo "This also won't run"
```

### `failure()`

True if any previous step failed:
```yaml
steps:
  - run: npm test
  - if: failure()
    run: ./notify-failure.sh
```

### `always()`

Always runs, regardless of success or failure:
```yaml
steps:
  - run: npm test
  - if: always()
    run: ./cleanup.sh
```

For jobs with dependencies:
```yaml
jobs:
  build:
    runs-on: ubuntu-latest

  cleanup:
    needs: build
    if: always()
    runs-on: ubuntu-latest
```

### `cancelled()`

True if workflow was cancelled:
```yaml
steps:
  - if: cancelled()
    run: echo "Workflow was cancelled"
```

## Common Conditional Patterns

### Run Only on Main Branch

```yaml
if: github.ref == 'refs/heads/main'
```

### Run Only on Pull Requests

```yaml
if: github.event_name == 'pull_request'
```

### Run Only on Tags

```yaml
if: startsWith(github.ref, 'refs/tags/')
```

### Skip on Forks

```yaml
if: github.repository == 'owner/repo'
```

### Run for Specific Actor

```yaml
if: github.actor == 'dependabot[bot]'
```

### Check PR Labels

```yaml
if: contains(github.event.pull_request.labels.*.name, 'deploy')
```

### Check Commit Message

```yaml
if: contains(github.event.head_commit.message, '[skip ci]') == false
```

### Run on Dependency Success

```yaml
jobs:
  deploy:
    needs: [build, test]
    if: needs.build.result == 'success' && needs.test.result == 'success'
```

### Continue on Dependency Failure

```yaml
jobs:
  report:
    needs: test
    if: always() && needs.test.result == 'failure'
```

## Matrix Strategy

### Basic Matrix

```yaml
jobs:
  test:
    strategy:
      matrix:
        node: [18, 20, 22]
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-node@<commit-sha>
        with:
          node-version: ${{ matrix.node }}
```

### Include Additional Combinations

```yaml
strategy:
  matrix:
    node: [18, 20]
    include:
      - node: 22
        os: ubuntu-latest
        experimental: true
```

### Exclude Combinations

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node: [18, 20]
    exclude:
      - os: windows-latest
        node: 18
```

### Fail-Fast Behavior

```yaml
strategy:
  fail-fast: false    # Continue other matrix jobs on failure
  matrix:
    node: [18, 20, 22]
```

### Max Parallel Jobs

```yaml
strategy:
  max-parallel: 2
  matrix:
    node: [18, 20, 22]
```

### Dynamic Matrix from JSON

```yaml
jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - id: set-matrix
        run: echo 'matrix=["a","b","c"]' >> $GITHUB_OUTPUT

  build:
    needs: prepare
    strategy:
      matrix:
        value: ${{ fromJSON(needs.prepare.outputs.matrix) }}
    runs-on: ubuntu-latest
```

## Expression Operators

### Comparison

```yaml
if: github.event.issue.number == 1
if: github.run_attempt > 1
if: matrix.node >= 20
```

### Logical

```yaml
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
if: ${{ !cancelled() }}
```

### Functions

```yaml
if: contains(github.event.pull_request.labels.*.name, 'urgent')
if: startsWith(github.ref, 'refs/tags/v')
if: endsWith(github.repository, '-template')
if: format('{0}/{1}', github.repository_owner, 'repo') == github.repository
if: join(github.event.pull_request.labels.*.name, ',') != ''
if: toJSON(github.event) != '{}'
if: fromJSON(needs.check.outputs.should_run)
if: hashFiles('**/package-lock.json') != ''
```

## Contexts Available in Conditionals

| Context | Description |
|---------|-------------|
| `github` | Workflow run information |
| `env` | Environment variables |
| `vars` | Configuration variables |
| `job` | Current job information |
| `steps` | Step outputs and status |
| `runner` | Runner information |
| `secrets` | Secret values |
| `needs` | Dependent job outputs |
| `matrix` | Matrix values |
| `inputs` | Workflow inputs |
