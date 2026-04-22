# Verification

The release is not finished until a downstream user has what they need to verify
it.

That means publishing verification data through the right channel, not just
generating it in CI. For GitHub-native attestations, the right channel is
GitHub's attestations API, or the OCI registry when registry-backed bundles are
needed. Do not attach raw provenance bundles to the release by default.

## What should ship with a release

At minimum, publish:

- the release artifacts themselves
- `checksums.txt`, when the release tool emits one
- SBOMs for shipped artifacts, or SBOM attestations when that is the consumer
  contract
- a digest map for published OCI artifacts such as `digests.txt`
- GitHub API-backed attestations tied to the final artifacts
- exact verification commands in the release notes, docs, or both

If the user has to reverse engineer your workflow to figure out what to verify,
the publishing design is incomplete.

Only ship raw Sigstore bundles, custom trusted roots, or detached signature
material as release assets when the project explicitly supports offline or
air-gapped verification.

## GitHub release integrity

For immutable GitHub releases, teach consumers to verify the release and the
local asset directly:

```bash
gh release verify v1.2.3 -R OWNER/REPO
gh release verify-asset v1.2.3 ./myapp_1.2.3_linux_amd64.tar.gz -R OWNER/REPO
```

This verifies that GitHub has a valid release attestation and that the local
asset digest matches the released asset. It is separate from build provenance.

## GitHub build provenance for release files

For a file published as a release asset, verify the GitHub API-backed
attestation directly. Do not require users to download a provenance bundle from
the release assets list.

```bash
gh attestation verify ./myapp_1.2.3_linux_amd64.tar.gz \
  --repo OWNER/REPO \
  --signer-workflow OWNER/REPO/.github/workflows/reusable-release.yml \
  --source-ref refs/tags/v1.2.3 \
  --deny-self-hosted-runners
```

If the release process has many file artifacts and emits a checksum manifest,
generate the attestation with `actions/attest` and `subject-checksums`:

```yaml
- name: Attest release artifacts
  uses: actions/attest@<full-commit-sha> # v4
  with:
    subject-checksums: dist/checksums.txt
```

If the attestation was produced by a reusable workflow, the reusable workflow is
the signer you should validate, not the caller workflow.

## GitHub attestation for an OCI artifact

Authenticate to the OCI registry first, then verify by digest:

```bash
gh attestation verify oci://ghcr.io/OWNER/IMAGE@sha256:<digest> \
  --repo OWNER/REPO \
  --signer-workflow OWNER/REPO/.github/workflows/reusable-release.yml \
  --source-ref refs/tags/v1.2.3 \
  --deny-self-hosted-runners
```

By default, `gh` fetches the attestation from GitHub. Add
`--bundle-from-oci` only when the release workflow intentionally pushed the
attestation bundle to the registry with `push-to-registry: true` and the
consumer should verify against that registry copy.

## Reusable workflow nuance

When you use a trusted reusable workflow, there are two workflow identities that
often matter:

- the reusable workflow that signed or attested the artifact
- the caller workflow that triggered it

`gh attestation verify` primarily validates the signer workflow identity. If you
need to constrain the caller workflow path as well, enforce that in policy:

- inspect `gh attestation verify --format json` output and apply additional
  checks, or
- enforce it in admission control or a policy engine on the consumer side

## Documentation rule

Every hardened release flow should leave behind copy-paste verification text.

Good places:

- GitHub release notes
- install or upgrade docs
- a verification section in the project README

Bad places:

- only inside workflow YAML comments
- only inside maintainer runbooks
- nowhere
