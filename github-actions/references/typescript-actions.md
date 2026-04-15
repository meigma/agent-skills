# Writing Custom TypeScript Actions

Custom JavaScript and TypeScript actions are privileged code. They run inside workflows that may hold tokens, cloud credentials, and repository write access. Keep logic in TypeScript, avoid shell interpolation with untrusted input, and prefer the narrowest token possible. For workflow-level trust boundaries, see [security-hardening.md](security-hardening.md).

## Security Rules

1. Keep untrusted input in TypeScript, not inline shell.
2. Never log tokens, private keys, or secret values.
3. Call `core.setSecret()` for derived credentials such as GitHub App installation tokens or signed JWTs.
4. Use `GITHUB_TOKEN` for repository-local operations, GitHub App tokens for escalation, and PATs only as a narrow fallback.
5. Publishing an action and consuming an action are different trust models: maintainers may move a major tag, but workflow consumers should still pin full commit SHAs.

## Project Setup

### Initialize Project

```bash
mkdir my-action && cd my-action
npm init -y
npm install @actions/core @actions/github
npm install -D typescript @types/node @vercel/ncc jest ts-jest @types/jest
```

### Directory Structure

```text
my-action/
├── action.yml
├── src/
│   └── index.ts
├── dist/
│   └── index.js
├── package.json
├── tsconfig.json
└── README.md
```

### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "outDir": "./lib",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "lib"]
}
```

### `package.json` Scripts

```json
{
  "scripts": {
    "build": "tsc && ncc build lib/index.js -o dist",
    "package": "npm run build",
    "test": "jest --runInBand"
  }
}
```

## Action Metadata (`action.yml`)

Use the currently supported Node runtime for JavaScript actions. The example below uses `node20`.

```yaml
name: 'PR Note'
description: 'Posts a note on a pull request'

inputs:
  github-token:
    description: 'Scoped token for GitHub API calls'
    required: true
  note:
    description: 'Message to post on the pull request'
    required: true
  dry-run:
    description: 'Validate inputs without making changes'
    required: false
    default: 'false'

outputs:
  result:
    description: 'Execution result'

runs:
  using: 'node20'
  main: 'dist/index.js'
```

## Action Implementation

### Safe Structure (`src/index.ts`)

```typescript
import * as core from '@actions/core';
import * as github from '@actions/github';

async function run(): Promise<void> {
  try {
    const token = core.getInput('github-token', { required: true });
    const note = core.getInput('note', { required: true, trimWhitespace: true });
    const dryRun = core.getBooleanInput('dry-run');
    const context = github.context;

    core.setSecret(token);
    core.info(`Repository: ${context.repo.owner}/${context.repo.repo}`);
    core.info(`Event: ${context.eventName}`);

    if (context.eventName !== 'pull_request') {
      core.notice('Not a pull_request event, skipping');
      core.setOutput('result', 'skipped');
      return;
    }

    const pullRequest = context.payload.pull_request;
    if (!pullRequest?.number) {
      core.setFailed('Could not determine pull request number');
      return;
    }

    if (dryRun) {
      core.notice('Dry run enabled; no comment created');
      core.setOutput('result', 'dry-run');
      return;
    }

    const octokit = github.getOctokit(token);
    await octokit.rest.issues.createComment({
      owner: context.repo.owner,
      repo: context.repo.repo,
      issue_number: pullRequest.number,
      body: note
    });

    core.setOutput('result', 'commented');
  } catch (error) {
    if (error instanceof Error) {
      core.setFailed(error.message);
      return;
    }

    core.setFailed('Unexpected error');
  }
}

void run();
```

## Handling Untrusted Input

Workflow context fields such as pull request titles, issue bodies, labels, branch names, and comments can be attacker-controlled.

Preferred approach:
- parse and validate in TypeScript
- pass data as structured values
- if you must invoke a process, pass arguments directly rather than interpolating into a shell command

Example:

```typescript
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);
const title = github.context.payload.pull_request?.title ?? '';

await execFileAsync('node', ['scripts/check-title.js', title]);
```

Avoid:
- `execSync("bash -lc \"echo " + title + "\"")`
- shell interpolation of untrusted values
- logging raw untrusted content when not necessary

## `@actions/core` API

### Inputs

```typescript
const name = core.getInput('name');
const requiredInput = core.getInput('required-input', { required: true });
const enabled = core.getBooleanInput('enabled');
const items = core.getMultilineInput('items');
```

### Outputs

```typescript
core.setOutput('result', 'success');
core.setOutput('data', JSON.stringify({ key: 'value' }));
```

### Logging

```typescript
core.debug('Debug message');
core.info('Info message');
core.notice('Notice message');
core.warning('Warning message');
core.error('Error message');
```

Do not log tokens or secret-bearing payloads.

### Secret Masking

Mask both source secrets and derived secrets:

```typescript
const apiKey = core.getInput('api-key', { required: true });
core.setSecret(apiKey);

const installationToken = 'derived-token-value';
core.setSecret(installationToken);
```

### Job Summary

```typescript
await core.summary
  .addHeading('Test Results')
  .addCodeBlock('npm test --coverage', 'bash')
  .write();
```

## `@actions/github` API

### Octokit Client

```typescript
const token = core.getInput('github-token', { required: true });
core.setSecret(token);
const octokit = github.getOctokit(token);
```

### Context Object

```typescript
const context = github.context;

context.eventName;
context.sha;
context.ref;
context.actor;
context.repo.owner;
context.repo.repo;
context.issue.number;
context.payload.pull_request?.number;
```

### Common Operations

```typescript
await octokit.rest.issues.createComment({
  ...github.context.repo,
  issue_number: github.context.issue.number,
  body: 'Comment from action'
});
```

## Token Guidance for Custom Actions

- Prefer `GITHUB_TOKEN` when the action only needs repository-local permissions.
- Prefer a GitHub App installation token when the action needs cross-repository access, stronger repository permissions, or intentional downstream workflow triggering.
- Use a PAT only if a GitHub App is not viable.

Document the minimum required permissions in the action README and workflow example.

## Building and Publishing

### Build the Action

```bash
npm run build
```

This compiles TypeScript and bundles with `ncc` into `dist/index.js`.

### Commit `dist/`

The compiled `dist/` folder must be committed for JavaScript actions:

```bash
git add dist/
git commit -m "Build action"
```

### Release Process for Action Maintainers

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

If you maintain the action, you may also move the major tag as part of your release process:

```bash
git tag -fa v1 -m "Update v1 tag"
git push origin v1 --force
```

Important distinction:
- action maintainers may move `v1`
- workflow consumers should still pin the action to a full commit SHA

For published release assets, prefer immutable releases and release provenance so downstream users can verify what was built.

## Testing

### Unit Tests with Jest

```typescript
import * as core from '@actions/core';
import * as github from '@actions/github';

jest.mock('@actions/core');
jest.mock('@actions/github');

describe('action', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('sets dry-run output', async () => {
    (core.getInput as jest.Mock).mockImplementation((name: string) => {
      if (name === 'github-token') return 'token';
      if (name === 'note') return 'hello';
      return '';
    });
    (core.getBooleanInput as jest.Mock).mockReturnValue(true);

    await import('./index');

    expect(core.setOutput).toHaveBeenCalledWith('result', 'dry-run');
  });
});
```

### Local Workflow Test

```yaml
name: Test Action

on:
  push:

permissions:
  contents: read
  pull-requests: write

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-commit-sha>  # vX.Y.Z
        with:
          persist-credentials: false
      - uses: ./
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          note: 'Test note'
          dry-run: 'true'
```
