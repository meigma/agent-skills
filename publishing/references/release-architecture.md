# Release Architecture

This skill assumes a publishing model with separate ownership boundaries:

1. a versioning workflow creates or updates the release PR
2. merging that PR creates a tag and an initial draft release
3. a tag workflow publishes artifacts, signs them, generates SBOMs, and creates
   attestations
4. only after those steps succeed does the workflow publish the draft release

That separation is the main design, not an implementation detail. It makes the
failure surface explicit and keeps immutable release settings workable.

## Default workflow shape

### 1. Versioning workflow

Run on pushes to the default branch.

Responsibilities:

- compute the next version
- update version-bearing files
- create or update the release PR
- after merge, create the tag and the initial draft release

Do not make this workflow publish packages, container images, charts, or
deployments.

### 2. Tag entrypoint workflow

Run on `push.tags: [v*]`.

Responsibilities:

- wait for the draft release created by the versioning workflow
- fail early if the tag and draft release do not match
- call the reusable publish workflow
- publish the existing draft release only after the reusable workflow succeeds

This workflow is the bridge between "a version now exists" and "artifacts are
now public and attestable".

### 3. Reusable publish workflow

The reusable workflow should own the actual publishing stages. A good default
split is:

- `scan-local`: build from the checked-out source, resolve local artifacts, and
  run scanners before publication
- `publish`: build and push real artifacts, resolve final digests, generate
  SBOMs, and upload release assets
- `attest-*`: create GitHub or registry-backed attestations from stable
  checksum and digest inputs

Treat the reusable workflow as the trusted builder. If consumers later verify
provenance, they should be verifying this workflow's identity.

### 4. Draft publication finalizer

The last job should flip the release from draft to published only after publish
and attestation succeed.

This is what keeps immutable releases sane: the draft exists early enough for
artifact uploads, but it never becomes public until the release is complete.

## Recommended concurrency

- versioning workflow: `cancel-in-progress: true`
- rehearsal workflow: `cancel-in-progress: false`
- tag publish workflow: `cancel-in-progress: false`

Canceling in-progress versioning runs is fine. Canceling in-progress release or
rehearsal runs is usually how you end up with half-published state.

## Minimal contract between jobs

The publish and attestation jobs need stable files, not inferred state.

Good contract files:

- `checksums.txt`
- `digests.txt`
- generated SBOM paths
- an env file or JSON file that records the final image/chart/artifact names and
  digests used by attestation jobs

If an attestation job needs to reconstruct artifact names from logs, the design
is too brittle.

## Generic tag workflow skeleton

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

permissions: {}

jobs:
  verify-draft-release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Wait for draft release handoff
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: ./scripts/wait-for-draft-release.sh

  release:
    needs: verify-draft-release
    uses: ./.github/workflows/reusable-release.yml
    permissions:
      contents: write
      packages: write
      id-token: write
      attestations: write
      artifact-metadata: write
    secrets:
      release_token: ${{ secrets.GITHUB_TOKEN }}

  publish-draft-release:
    needs: release
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Publish existing draft release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: ./scripts/publish-draft-release.sh
```

The reusable workflow can use any build tool. GoReleaser is a good fit for Go
projects, but the architecture above is meant to outlive the choice of builder.
