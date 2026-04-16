# Verification

The release is not finished until a downstream user has what they need to verify
it.

That means publishing the verification materials, not just generating them in
CI.

## What should ship with a release

At minimum, publish:

- the release artifacts themselves
- `checksums.txt`
- a Cosign bundle or equivalent signature material for `checksums.txt`
- SBOMs for shipped artifacts
- a digest map for published OCI artifacts such as `digests.txt`
- GitHub or registry-backed attestations tied to the final artifacts
- exact verification commands in the release notes, docs, or both

If the user has to reverse engineer your workflow to figure out what to verify,
the publishing design is incomplete.

## Checksums and signature bundle

For GitHub Actions keyless signing, prefer an exact workflow identity rather
than a loose repository-wide regex.

Example:

```bash
cosign verify-blob \
  --bundle checksums.txt.sigstore.json \
  --certificate-identity "https://github.com/OWNER/REPO/.github/workflows/release.yml@refs/tags/v1.2.3" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  checksums.txt

sha256sum -c checksums.txt --ignore-missing
```

This verifies two different things:

- the checksum manifest was signed by the expected workflow identity
- the downloaded artifacts match the published checksums

## GitHub artifact attestation for a released file

For a file published as a release asset:

```bash
gh attestation verify myapp_1.2.3_linux_amd64.tar.gz \
  --repo OWNER/REPO \
  --signer-workflow OWNER/REPO/.github/workflows/reusable-release.yml \
  --source-ref refs/tags/v1.2.3 \
  --deny-self-hosted-runners
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
  --bundle-from-oci \
  --deny-self-hosted-runners
```

The same pattern applies to other OCI artifacts, including charts, as long as
you verify the final digest and fetch the attestation bundle from the registry.

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
