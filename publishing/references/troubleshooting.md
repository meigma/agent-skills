# Troubleshooting

These are the failure modes that tend to appear after the release PR is merged,
which is exactly why this skill treats rehearsal as mandatory.

## Draft release not found right after tag push

Symptom:

- the tag workflow starts but cannot see the draft release that the versioning
  workflow was supposed to create

Cause:

- GitHub release handoff is eventually consistent

Fix:

- poll the Releases API for the tag and draft state before proceeding
- avoid assuming `gh release view <tag>` will succeed immediately

## Tag exists, but downstream publish workflow never ran

Symptom:

- Release Please merged, the version bumped, but the publish workflow did not
  trigger from the created tag

Cause:

- the tag was created with a token that does not trigger downstream workflows

Fix:

- prefer a GitHub App installation token for the versioning workflow when the
  created tag must start a new workflow

## Immutable release settings reject uploads

Symptom:

- publish job fails when trying to create or mutate a release

Cause:

- the workflow is trying to create a second release or mutate a published one
  after immutable release protections apply

Fix:

- have the versioning workflow create the initial draft release
- have the publish workflow reuse that existing draft
- only flip the draft to published after all uploads and attestations succeed

## Fresh tags or rehearsal versions fail to build

Symptom:

- a just-created tag or synthetic rehearsal version fails because a package or
  module index has not caught up yet

Cause:

- the builder depends on remote indexing rather than the checked-out source tree

Fix:

- build from the checked-out source tree when the tool supports it
- for GoReleaser, disabling `gomod.proxy` can be the correct tradeoff for fresh
  tag and rehearsal reliability

## Local scan cannot find the release-candidate image

Symptom:

- Trivy or another scanner cannot find the locally built image during rehearsal
  or pre-publish scanning

Cause:

- the workflow guessed image references from a version string instead of reading
  the builder outputs

Fix:

- resolve the actual local image names from build metadata such as
  `dist/artifacts.json`
- scan those exact references

## OCI attestation push fails in a later job

Symptom:

- the publish job succeeded, but the OCI attestation job fails to push or verify

Cause:

- registry login state does not carry across jobs

Fix:

- log into the registry again in the attestation job before pushing or fetching
  OCI-backed attestation bundles

## Helm or OCI digest parsing is empty

Symptom:

- the workflow pushed an artifact, but the parsed digest is blank

Cause:

- CLI output changed shape, included ANSI color codes, or wrote the digest on
  stderr

Fix:

- capture combined output
- strip ANSI control sequences
- parse on a stable label such as `Digest:`
- fail fast if the digest is empty

## Provenance verification is checking the wrong workflow

Symptom:

- verification fails even though the attestation exists

Cause:

- the repo uses a reusable workflow as the trusted builder, but verification is
  checking the caller workflow identity instead

Fix:

- verify the reusable workflow as the signer
- if policy also needs to constrain the caller workflow path or ref, enforce
  that separately through JSON inspection or admission policy
