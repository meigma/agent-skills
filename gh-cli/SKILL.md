---
name: gh-cli
description: >
  Use GitHub CLI (`gh`) for repository, pull request, issue, and GitHub Actions
  workflows. Use when a task mentions `gh`, GitHub CLI, `gh pr`, `gh run`,
  `gh issue`, `gh repo`, or `gh api`, or when you need to inspect or operate
  GitHub from the terminal. Prefer high-level `gh` subcommands first; use
  `gh api` only when the CLI does not expose the operation directly.
---

# GitHub CLI

Use this skill as an operator guide for GitHub's official CLI. Ground advice in
the current local `gh` help and the official manual, not memory.

## Verified against

- Manual: https://cli.github.com/manual
- Local CLI used for command grounding: `gh 2.88.1`

## Use this skill when

- You need to create, review, merge, or update pull requests from the terminal.
- You need to inspect or operate GitHub Actions runs and workflows without
  opening the browser first.
- You need to create or manage issues, labels, assignments, or milestones.
- You need to inspect or change repository settings, secrets, variables, or
  rulesets.
- You need a precise GitHub API call and the higher-level `gh` commands are not
  enough.

## Default stance

1. Prove auth and repo context first: `gh auth status`, then either use
   `-R owner/repo` explicitly or verify `gh repo set-default --view`.
2. Prefer the highest-level subcommand that matches the task:
   - `gh pr` for pull requests
   - `gh run` and `gh workflow` for Actions
   - `gh issue` for issues
   - `gh repo`, `gh secret`, `gh variable`, and `gh ruleset` for repo-level work
3. Prefer `--json` with `--jq` or `--template` for automation and agent flows.
   Do not scrape human-oriented table output if JSON is available.
4. Use `--web` when the browser materially improves the task, such as large diffs
   or visually dense logs, but keep the default path terminal-first.
5. Treat `gh api` as the break-glass path for unsupported operations, bulk reads,
   GraphQL queries, previews, or exact payload control.

## Fast orientation

Start here when you have little or no context:

```bash
gh --version
gh auth status
gh repo set-default --view
gh repo view --json nameWithOwner,defaultBranchRef,viewerPermission
gh pr status
gh status
```

If you are outside a cloned repository, use `-R owner/repo` on every command or
set `GH_REPO=owner/repo`.

## Command surface

Use these command families as the main mental model:

- `gh auth`, `gh config`, `gh repo set-default`, `gh status`, `gh browse`:
  authentication, local targeting, and general orientation.
- `gh pr`: create, inspect, review, update, and merge pull requests.
- `gh issue`: create, inspect, edit, comment on, close, reopen, transfer, and
  pin issues.
- `gh workflow`, `gh run`: discover workflows, trigger dispatches, and inspect,
  watch, rerun, cancel, or download workflow runs.
- `gh repo`, `gh secret`, `gh variable`, `gh ruleset`: repository settings and
  operational controls.
- `gh search`, `gh release`, `gh label`, `gh org`, `gh project`: adjacent GitHub
  workflows when needed.
- `gh api`: direct REST and GraphQL access.

For a concise command map, see [references/commands.md](references/commands.md).

## Core workflows

### 1. Creating and managing pull requests

#### Create a pull request

Push the branch first, then create the PR:

```bash
git push -u origin HEAD
gh pr create --fill
```

Use explicit metadata when you want deterministic output:

```bash
gh pr create \
  --base main \
  --title "Fix flaky CI retry logic" \
  --body-file .github/pull_request_template.md \
  --reviewer my-org/platform \
  --label bug
```

Notes:

- `gh pr create` defaults the head branch to the current branch.
- `--fill`, `--fill-first`, and `--fill-verbose` pull from commit history.
- `--draft` is the right default when CI or review is not ready yet.
- `--head user:branch` is the escape hatch for cross-fork PR creation.
- Adding a PR to Projects requires `gh auth refresh -s project`.

#### Inspect and update a pull request

Use the PR-native commands before falling back to runs or raw API calls:

```bash
gh pr view 123 --comments
gh pr diff 123
gh pr checks 123 --required
gh pr review 123 --comment -b "Please split the config change from the refactor."
gh pr edit 123 --title "Tighten Actions token scope"
gh pr update-branch 123
gh pr ready 123
```

For machine-friendly state:

```bash
gh pr view 123 \
  --json number,title,isDraft,reviewDecision,mergeStateStatus,mergeable,statusCheckRollup,url
```

Use `gh pr status` when you want the set of PRs relevant to you in the current
repository. Use `gh status` when you need a broader cross-repo inbox view.

#### Merge a pull request

Default to the repository's normal merge strategy and protection rules. Make the
strategy explicit when it matters:

```bash
gh pr merge 123 --squash --delete-branch
gh pr merge 123 --rebase --delete-branch
gh pr merge 123 --merge --delete-branch
```

For safer automation, pin the head SHA:

```bash
gh pr merge 123 --squash --delete-branch --match-head-commit "$EXPECTED_SHA"
```

Important behavior:

- Without an argument, `gh pr merge` targets the PR for the current branch.
- On repositories using a merge queue, `gh pr merge` will add the PR to the
  queue or enable auto-merge as required.
- `--auto` is the right choice when checks or reviews are still pending.
- `--admin` bypasses protections and should be reserved for explicit break-glass
  situations.
- `gh pr revert`, `gh pr close`, and `gh pr reopen` cover the common recovery
  paths after review or merge decisions change.

### 2. Watching and investigating CI runs

#### From zero context

When you do not yet know which workflow or run matters, start wide and narrow:

```bash
gh workflow list --all
gh run list --limit 20
gh run list --workflow CI --branch main --json databaseId,workflowName,status,conclusion,headBranch,displayTitle,url
```

Once you have a run ID:

```bash
gh run view 123456
gh run view 123456 --verbose
gh run view 123456 --log-failed
gh run watch 123456 --compact --exit-status
```

Operational follow-ups:

```bash
gh run rerun 123456
gh run cancel 123456
gh run download 123456
gh workflow run ci.yml --ref my-branch -f shard=2
```

Notes:

- `gh workflow run` only works for workflows that support `workflow_dispatch`.
- `gh run watch` requires auth that can read checks; its help notes that it does
  not work with fine-grained PAT authentication.
- `gh run view --log` and `--log-failed` are the first stop for terminal log
  inspection before resorting to the browser.

#### From an existing pull request

If you already have a PR number or branch, stay PR-centric first:

```bash
gh pr checks 123
gh pr checks 123 --watch --fail-fast
gh pr view 123 --json number,headRefName,headRefOid,statusCheckRollup,url
```

Then pivot into workflow runs when you need deeper log or job detail:

```bash
gh run list --branch my-branch --limit 10
gh run list --commit <head-sha> --limit 10
gh run view <run-id> --log-failed
gh run view --job <job-id> --log
```

Useful behavior:

- `gh pr checks` is the fastest PR-specific signal for pass, fail, and pending.
- In watch mode, `gh pr checks` exits with code `8` when checks are still
  pending. Use that in automation instead of guessing from text output.
- `gh run view --exit-status` gives a simple non-zero exit on failed runs.

### 3. Creating and managing issues

Start with filtered list and view operations:

```bash
gh issue list --state open --label bug
gh issue list --search "is:open sort:updated-desc label:ci"
gh issue view 456 --comments
```

Create issues with explicit metadata when you can:

```bash
gh issue create \
  --title "CI flakes on macOS arm64" \
  --body-file /tmp/issue.md \
  --label bug \
  --assignee "@me" \
  --milestone "Q2"
```

Manage existing issues in place:

```bash
gh issue edit 456 --add-label triage --remove-label needs-info
gh issue comment 456 -b "Root cause identified. Working on a fix."
gh issue close 456
gh issue reopen 456
gh issue transfer 456 other-owner/other-repo
```

Notes:

- `gh issue develop` exists for managing linked branches.
- Adding issues to Projects also requires `gh auth refresh -s project`.
- Prefer `--body-file` over long inline strings when an agent is generating
  multi-paragraph issue bodies.

### 4. Managing repository settings

Inspect first, then mutate:

```bash
gh repo view owner/repo --json \
  nameWithOwner,visibility,defaultBranchRef,deleteBranchOnMerge,mergeCommitAllowed,rebaseMergeAllowed,squashMergeAllowed,viewerPermission
gh ruleset list -R owner/repo
gh ruleset check main -R owner/repo
```

Use `gh repo edit` for the common repository controls:

```bash
gh repo edit owner/repo \
  --default-branch main \
  --delete-branch-on-merge \
  --enable-auto-merge \
  --enable-issues=true \
  --enable-projects=false
```

Common settings operations:

```bash
gh repo edit owner/repo --add-topic cli --remove-topic legacy
gh repo edit owner/repo --description "Internal build orchestration service"
gh repo edit owner/repo --visibility private --accept-visibility-change-consequences
```

Secrets and variables live in their own command groups:

```bash
gh secret list -R owner/repo
gh secret set AWS_ROLE_ARN -R owner/repo --body "$AWS_ROLE_ARN"
gh secret set PROD_TOKEN --env production -R owner/repo < token.txt

gh variable list -R owner/repo
gh variable set DEPLOY_REGION -R owner/repo --body us-west-2
gh variable set IMAGE_TAG --env production -R owner/repo --body stable
```

Important nuance:

- `gh repo set-default` helps most PR, issue, release, and Actions commands, but
  it does not apply to secret management. Use `-R owner/repo` explicitly for
  `gh secret` and `gh variable`.
- `gh repo edit` toggles settings off with `--flag=false`.
- `gh ruleset` currently covers inspection. Use `gh api` when you need to create
  or update rulesets or other settings not exposed by `gh repo edit`.

### 5. Break glass with `gh api`

Use `gh api` only when the purpose-built commands are missing a field, mutation,
preview, or bulk traversal you need.

Prefer this escalation path:

1. Try the highest-level command with `--json`.
2. If the command lacks the field or operation, switch to `gh api`.
3. Stay structured: JSON in, JSON out, `--jq` or `--template` for reduction.

#### REST examples

```bash
gh api repos/{owner}/{repo}/pulls/123
gh api repos/{owner}/{repo}/issues/456/comments -f body='Investigating now.'
gh api repos/{owner}/{repo}/actions/runs --paginate --slurp
```

#### GraphQL example

```bash
gh api graphql \
  -F owner='{owner}' \
  -F name='{repo}' \
  -F number=123 \
  -f query='
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) {
        pullRequest(number: $number) {
          number
          title
          mergeStateStatus
          reviewDecision
        }
      }
    }
  '
```

#### Rules for `gh api`

- Use `{owner}`, `{repo}`, and `{branch}` placeholders instead of string-building
  those values yourself when repo context is available.
- Use `-f` for raw strings and `-F` for typed values, nested fields, arrays, and
  file/stdin reads with `@path` or `@-`.
- Use `--method GET` when you add fields to a read request and still want query
  parameters instead of a POST body.
- Use `--input file.json` for large request bodies or exact payload control.
- Use `--paginate` and optionally `--slurp` for multi-page REST or GraphQL
  traversals.
- Use `--preview` or `-H` only when the endpoint explicitly requires it.
- Keep `--verbose` for troubleshooting the transport itself, not for normal
  automation.

## Maintenance checklist

Re-verify this skill when `gh` releases a new minor or major version:

1. Re-run locally:
   - `gh --version`
   - `gh help`
   - `gh auth status --help`
   - `gh pr --help`
   - `gh pr create --help`
   - `gh pr merge --help`
   - `gh pr checks --help`
   - `gh run --help`
   - `gh run list --help`
   - `gh run view --help`
   - `gh run watch --help`
   - `gh workflow --help`
   - `gh workflow run --help`
   - `gh issue --help`
   - `gh issue create --help`
   - `gh issue edit --help`
   - `gh repo --help`
   - `gh repo edit --help`
   - `gh repo set-default --help`
   - `gh ruleset --help`
   - `gh secret --help`
   - `gh variable --help`
   - `gh api --help`
2. Re-open the official manual: https://cli.github.com/manual
3. Delete or rewrite any recommendation that is no longer grounded in the local
   CLI help or the manual.
