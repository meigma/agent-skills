---
name: publishing
description: Designs hardened release and publishing workflows that separate versioning from publication, require rehearsals before real releases, and ship signed, attestable artifacts with a SLSA Level 3 target.
---

# Publishing

Use this skill when the user wants a reusable publishing architecture rather
than just a tool-specific setup. It is for release pipelines that need to
survive the real failure surface: eventual consistency between tags and
releases, immutable release settings, registry pushes, signing, SBOMs,
attestations, and post-release rescans.

This skill is tool-agnostic. The examples below may use GitHub Actions, Release
Please, OCI registries, Helm, and GoReleaser, but the core pattern applies to
any project that can:

- compute a version
- publish immutable artifacts
- resolve final digests
- publish provenance records that consumers can verify later

## Default stance

1. Separate version orchestration from publication.
2. Treat a rehearsal workflow as mandatory when changing release automation or
   before merging a release PR.
3. Publish into an existing draft release and make it public only after
   publishing, signing, SBOM generation, and attestation succeed.
4. Aim for SLSA Level 3 oriented provenance using a trusted reusable workflow,
   short-lived credentials, and digest-based attestations.
5. Keep security checks continuous in CI and scheduled rescans, not just in the
   tagged release job.
6. Give downstream users exact verification commands. Do not attach raw
   attestation bundles as release assets unless offline verification requires
   them.

## Read these files as needed

- [references/release-architecture.md](references/release-architecture.md) for the default workflow
  structure and job boundaries
- [references/release-please.md](references/release-please.md) only when Release Please is in scope
- [references/rehearsal.md](references/rehearsal.md) for the mandatory rehearsal pattern
- [references/security.md](references/security.md) for SLSA-oriented hardening, continuous adherence,
  and consumer enforcement
- [references/verification.md](references/verification.md) for what must ship with a release,
  what should live in GitHub's attestation service, and how users verify it
- [references/troubleshooting.md](references/troubleshooting.md) for the failure modes that show up
  after merge if the design is too optimistic

If the implementation uses GoReleaser, also use the `goreleaser` skill. This
skill teaches the publishing architecture around the build tool, not the build
tool itself.

## Working rules for agents

- Do not collapse release PR creation, tagging, publishing, and deployment into
  one workflow when the repo wants a hardened reusable pattern.
- Prefer a dedicated tag-triggered publish workflow, or an equivalent immutable
  release event, over inlining publish work inside the versioning job.
- Prefer a GitHub App token for the versioning workflow when created tags must
  trigger downstream workflows or bypass repository rulesets.
- Pin every third-party action to a full commit SHA, set `permissions: {}` at
  the workflow level, and only grant the scopes each job actually needs.
- Keep `persist-credentials: false` on checkouts unless a step truly needs git
  write-back.
- Pass checksums, digests, SBOMs, and attestation metadata across jobs as
  workflow artifacts or files. Do not make them release assets unless the
  project explicitly supports offline verification. Do not depend on parsing job
  logs later.
- Attest and verify digests, not tags.
- For GitHub-native provenance, prefer `actions/attest` pinned to a full commit
  SHA. GitHub's `actions/attest-build-provenance` v4 path is a compatibility
  wrapper; new workflows should use `actions/attest` directly.
- Let GitHub-native attestation actions upload provenance to GitHub's
  attestations API. Do not upload the generated Sigstore bundles as release
  assets by default.
- For many release files, use a checksum file as the `subject-checksums` input.
  For OCI artifacts, use the final `subject-name` and `subject-digest`; set
  `push-to-registry: true` only when you also want registry-backed attestations
  or linked-artifact storage records.
- Rehearsals should stay faithful to the real publish path. Prefer a synthetic
  version and a safe draft/publication toggle over a fake dry run that skips the
  interesting failure modes.
- When in doubt, optimize for rehearsal fidelity and user verification quality
  over a shorter workflow.
