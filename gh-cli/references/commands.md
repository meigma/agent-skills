# `gh` command map

This is a compact command map for the GitHub CLI families that matter most in
agent workflows. It is intentionally grouped by job-to-be-done rather than
trying to reproduce the entire manual.

## Orientation and targeting

- `gh auth`: authenticate, inspect auth state, switch accounts, refresh scopes.
- `gh config`: inspect or change local `gh` behavior.
- `gh repo set-default`: bind the current directory to a default GitHub repo for
  PR, issue, release, and Actions commands.
- `gh status`: cross-repo inbox for assigned issues, assigned PRs, review
  requests, mentions, and repo activity.
- `gh browse`: jump to the corresponding browser view when terminal output is not
  enough.

## Pull requests

- `gh pr create`: create PRs from the current or specified head branch.
- `gh pr status`: summarize PRs relevant to you in the current repository.
- `gh pr list`, `gh pr view`, `gh pr diff`: read PR state and changes.
- `gh pr checks`: read and watch PR-specific CI state.
- `gh pr comment`, `gh pr review`: leave comments or review states.
- `gh pr edit`, `gh pr ready`, `gh pr update-branch`: update metadata and branch
  freshness.
- `gh pr merge`, `gh pr close`, `gh pr reopen`, `gh pr revert`: finish or undo
  the PR lifecycle.

## Issues

- `gh issue create`: create new issues, optionally with labels, assignees,
  milestones, and projects.
- `gh issue status`: summarize issues relevant to you.
- `gh issue list`, `gh issue view`: inspect issue state and comments.
- `gh issue edit`, `gh issue comment`: update existing issues.
- `gh issue close`, `gh issue reopen`, `gh issue pin`, `gh issue unpin`: manage
  issue lifecycle and visibility.
- `gh issue transfer`: move issues across repositories.
- `gh issue develop`: manage linked branches for issue work.

## GitHub Actions

- `gh workflow list`, `gh workflow view`: discover workflows.
- `gh workflow run`: trigger `workflow_dispatch` workflows.
- `gh workflow enable`, `gh workflow disable`: change workflow availability.
- `gh run list`: enumerate recent workflow runs.
- `gh run view`: inspect run summary, jobs, steps, and logs.
- `gh run watch`: stream progress until completion.
- `gh run rerun`, `gh run cancel`, `gh run delete`, `gh run download`: operate
  on existing runs and artifacts.
- `gh cache`: inspect or clean Actions caches when that is part of debugging.

## Repository administration

- `gh repo view`: inspect repo metadata and policy-relevant fields.
- `gh repo edit`: change common repo settings such as default branch, merge
  options, visibility, topics, issues, projects, wiki, auto-merge, and secret
  scanning.
- `gh repo clone`, `gh repo fork`, `gh repo sync`: materialize or reconcile
  repository state locally.
- `gh repo create`, `gh repo rename`, `gh repo archive`, `gh repo unarchive`,
  `gh repo delete`: repo lifecycle operations.
- `gh ruleset`: inspect active rulesets and branch applicability.
- `gh secret`: set, list, and delete repository, environment, organization, and
  user secrets.
- `gh variable`: set, list, get, and delete repository, environment, and
  organization variables.

## Search and adjacent workflows

- `gh search`: search repositories, issues, and pull requests.
- `gh label`: manage labels.
- `gh release`: inspect or operate release objects.
- `gh project`: work with GitHub Projects.
- `gh org`: inspect and manage organization-level resources.

## Escape hatches

- `gh api`: direct GitHub REST and GraphQL access with auth, pagination,
  templating, and typed field support.
- `gh alias`: create local shorthand commands for repetitive workflows.
- `gh extension`: install or manage extensions when the core CLI does not cover
  a workflow cleanly.

## Practical rule

Prefer command families in this order:

1. Resource-specific command such as `gh pr`, `gh issue`, `gh run`, or `gh repo`
2. Related support command such as `gh workflow`, `gh ruleset`, `gh secret`, or
   `gh variable`
3. `gh api` for direct REST or GraphQL access
