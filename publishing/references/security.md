# Security, Provenance, and Continuous Adherence

This skill targets SLSA Level 3 oriented publishing. In practice that means:

- trusted, reusable build logic
- short-lived credentials instead of long-lived secrets where possible
- immutable artifact identities based on digests
- attestations that consumers can verify later
- continuous checks that keep the release path honest between releases

## Workflow hardening baseline

Start here for every publishing workflow:

- set `permissions: {}` at the workflow level
- grant job-level scopes narrowly
- pin every third-party action to a full commit SHA
- use `persist-credentials: false` on checkout
- prefer OIDC and keyless signing over static signing keys
- prefer `GITHUB_TOKEN`, then GitHub App tokens, and use PATs only when truly
  necessary

Typical publish job permissions:

- `contents: write` for draft release asset uploads or release mutation
- `packages: write` for OCI pushes
- `id-token: write` for keyless signing and attestations
- `attestations: write` and `artifact-metadata: write` for GitHub-native
  attestation flows

## Pre-publish local scanning

Before publishing real artifacts, build from the checked-out source and scan the
local release candidate.

Why:

- it catches vulnerable or malformed artifacts before they hit the registry
- it exercises the same builder inputs the real release will use
- it keeps publish failures closer to the code change that caused them

Do not guess local image names. Resolve them from builder output metadata, then
scan those exact references.

## Continuous adherence

A hardened release path also needs ongoing checks outside of the tag workflow.

Good defaults:

- CI runs snapshot builds and publish-tool config validation
- CI runs vulnerability scanning against release-candidate artifacts
- CI runs workflow linting such as `actionlint`
- a scheduled rescan checks the latest published image and opens or updates a
  tracking issue when new HIGH or CRITICAL findings appear

This matters because the release can be clean at publish time and still age into
an unsafe state later.

## Attestation strategy

Use stable files as the bridge between publish and attest jobs:

- `checksums.txt` for released files
- `digests.txt` for OCI artifacts
- an env or JSON file for final artifact names and digests

Then create attestations from those stable inputs rather than reconstructing
state in each job.

For GitHub-native attestations:

- attest released files from `checksums.txt`
- attest OCI artifacts by resolved digest, not by tag
- if the registry-backed attestation step runs in a separate job, log back into
  the registry there too

## Consumer enforcement

Publishing is stronger when the consumer side can enforce what you shipped.

Reusable patterns:

- embed default digests into deployment manifests or chart metadata so the
  deployed image is pinned by default
- optionally render an admission policy that requires digest pinning, signature
  verification, and provenance verification
- if you use a reusable workflow as the trusted builder, make the admission
  policy verify that workflow identity precisely

If you teach an admission policy, default it to audit mode first. The point is
to make enforcement adoptable, not to surprise operators with an outage.
