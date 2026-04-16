# Rehearsal

Rehearsal is mandatory in this design.

If the release path has changed, or if a release PR is about to be merged, the
correct question is not "does the config look right?" It is "can the real
publish path complete end to end without making a public release?"

## What rehearsal must exercise

A rehearsal should reuse the real publish workflow and keep these parts real:

- build steps
- registry authentication
- registry pushes
- digest resolution
- signing
- SBOM generation
- attestation creation

The safe differences are:

- use a synthetic version instead of the final release version
- disable GitHub release creation or mutation
- skip uploading assets into the public draft release when that would create
  confusing public state

If a rehearsal skips the interesting failure modes, it is not a rehearsal. It
is a syntax check.

## Recommended trigger and versioning

Use `workflow_dispatch` with an optional `release_version` input. If the user
does not provide one, compute a synthetic prerelease version from the run number
and commit SHA.

Example:

```yaml
name: Release Rehearsal

on:
  workflow_dispatch:
    inputs:
      release_version:
        description: Optional synthetic SemVer without the leading v
        required: false
        type: string

jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      release_version: ${{ steps.version.outputs.value }}
    steps:
      - name: Compute rehearsal version
        id: version
        run: |
          if [ -n "${{ inputs.release_version }}" ]; then
            version="${{ inputs.release_version }}"
          else
            short_sha="$(printf '%s' "${GITHUB_SHA}" | cut -c1-7)"
            version="0.0.0-rc.${GITHUB_RUN_NUMBER}.${short_sha}"
          fi
          echo "value=${version}" >> "${GITHUB_OUTPUT}"

  rehearsal:
    needs: prepare
    uses: ./.github/workflows/reusable-release.yml
    with:
      release_version: ${{ needs.prepare.outputs.release_version }}
      disable_github_release: true
      upload_release_assets: false
    secrets:
      release_token: ${{ secrets.GITHUB_TOKEN }}
```

## Rehearsal checklist

Before calling a rehearsal successful, confirm that it exercised:

- the same reusable publish workflow as the real release
- the same registry logins and push operations
- the same signing and SBOM tooling
- the same attestation jobs and permissions
- the same artifact-to-digest resolution logic

## Common anti-patterns

- A fake dry run that skips registry pushes
- A fake version that is not valid SemVer for downstream tooling
- A rehearsal workflow that duplicates the real workflow instead of calling it
- Scanning guessed image tags instead of the actual locally built image
  references produced by the builder

Rehearsal exists because release failures after merge are expensive. Design the
workflow like you expect it to save you from that exact problem.
