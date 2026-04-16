# Release Please In This Model

Use this file when the versioning side of the publishing architecture uses
Release Please.

The important point is scope: Release Please owns the release PR, tag, and
initial draft release. The dedicated tag workflow owns publication, signing,
SBOMs, and attestations.

## Why `simple` is often the safest default

For single-version repositories that ship more than one thing, `release-type:
simple` is often the best fit.

Typical cases:

- application plus OCI image
- binary plus Helm chart
- library plus documentation site
- any polyglot repo where one SemVer governs multiple outputs

`simple` keeps the versioning contract explicit and works well with
`extra-files`.

## Baseline config

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "draft": true,
  "force-tag-creation": true,
  "release-type": "simple",
  "include-v-in-tag": true,
  "packages": {
    ".": {
      "extra-files": [
        {
          "type": "yaml",
          "path": "chart/Chart.yaml",
          "jsonpath": "$.version"
        },
        {
          "type": "yaml",
          "path": "chart/Chart.yaml",
          "jsonpath": "$.appVersion"
        }
      ]
    }
  }
}
```

What matters here:

- `draft: true`: the tag workflow publishes into the draft and flips it public
  only after success
- `force-tag-creation: true`: useful when the repo has history or tag edge
  cases, but it may require ruleset bypass
- `include-v-in-tag: true`: keeps tag-triggered workflows and verification text
  consistent
- `extra-files`: update every version-bearing file that consumers actually see

## Token model

If merging the Release Please PR must create a tag that triggers another
workflow, prefer a GitHub App installation token over the default
`GITHUB_TOKEN`.

Reasons:

- downstream workflows are more reliable when the tag is created by an actor
  that is allowed to trigger them
- repository tag rulesets may require bypass permissions
- the permission boundary is clearer than widening the default token everywhere

## Workflow skeleton

```yaml
name: Release Please

on:
  push:
    branches:
      - main

permissions: {}

jobs:
  release-please:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
    steps:
      - name: Mint GitHub App token
        id: app-token
        uses: actions/create-github-app-token@<full-commit-sha>
        with:
          app-id: ${{ secrets.RELEASE_APP_ID }}
          private-key: ${{ secrets.RELEASE_APP_PRIVATE_KEY }}

      - name: Run Release Please
        id: release
        uses: googleapis/release-please-action@<full-commit-sha>
        with:
          token: ${{ steps.app-token.outputs.token }}
          target-branch: main
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json
```

## Agent guidance

- Prefer manifest configuration files over ad hoc version bump scripts.
- Keep the versioning workflow free of publish logic.
- If the repo has multiple packages with independent versioning, use the
  existing `release-please` skill for monorepo-specific patterns.
- If the repo needs the hardened publishing design from this skill, do not rely
  solely on `release_created` outputs from the same workflow. Let the created
  tag trigger the publish path.
