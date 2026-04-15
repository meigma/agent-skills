# SBOMs, Verifiable Builds, and Attestations

Use this file when the release pipeline needs stronger provenance and dependency transparency.

Sources:
- https://goreleaser.com/customization/sbom/
- https://goreleaser.com/customization/builds/verifiable_builds/
- https://goreleaser.com/customization/attestations/
- https://docs.github.com/en/actions/concepts/security/artifact-attestations
- https://oss.anchore.com/docs/installation/syft/

## Secure default

For public releases, prefer this combination:

- `gomod.proxy: true` for verifiable tagged builds
- `sboms:` for archive SBOMs
- Cosign keyless signing for `checksums.txt`
- GitHub artifact attestations generated from `checksums.txt`

Cosign signing and GitHub artifact attestations are complementary:

- Cosign bundles are portable and easy to verify offline
- GitHub artifact attestations add signed provenance with GitHub-native enforcement and policy hooks

## Baseline config

```yaml
version: 2

gomod:
  proxy: true
  env:
    - GOPROXY=https://proxy.golang.org,direct
    - GOSUMDB=sum.golang.org

checksum:
  name_template: checksums.txt

sboms:
  - artifacts: archive
```

Notes:

- `gomod.proxy` only applies to tagged releases. Snapshots ignore it.
- verifiable builds embed module information that users can inspect with `go version -m`.
- GoReleaser SBOMs default to Syft and default to SPDX JSON for archive artifacts.

## Installing Syft safely

Prefer one of these paths:

- CI: pinned `anchore/sbom-action/download-syft` action
- local development on macOS: `brew install syft`
- other environments: use an official package or the official installer only with verification enabled

If you must use Anchore's installer, require signature verification and make sure `cosign` is already installed before running it. Do not teach raw unverified `curl | sh`.

Source: https://oss.anchore.com/docs/installation/syft/

## GitHub artifact attestations

To attest released files from `checksums.txt`, the workflow needs:

- `attestations: write`
- `id-token: write`
- a step using `actions/attest` after GoReleaser finishes

Example step:

```yaml
- name: Attest released files listed in checksums.txt
  uses: actions/attest@59d89421af93a897026c735860bf21b6eb4f7b26 # v4.1.0
  with:
    subject-checksums: ./dist/checksums.txt
```

If the release also publishes container images, set a predictable `docker_digest.name_template`, then attest `./dist/digests.txt` as well.

## Verification commands

Inspect verifiable build metadata:

```bash
go version -m ./dist/myapp_darwin_arm64/myapp
```

Verify a released artifact against GitHub attestations with precise signer constraints:

```bash
gh attestation verify myapp_1.2.3_linux_amd64.tar.gz \
  --repo OWNER/REPO \
  --signer-workflow OWNER/REPO/.github/workflows/release.yml \
  --source-ref refs/tags/v1.2.3 \
  --deny-self-hosted-runners
```

If the artifact was attested by a reusable workflow, verify the reusable workflow identity instead of the caller workflow.

Source references:
- https://docs.github.com/en/actions/concepts/security/artifact-attestations
- local validation: `gh attestation verify --help`

## Practical guidance

- Generate SBOMs for shipped archives by default.
- Use SPDX JSON unless a downstream consumer requires CycloneDX.
- Keep `gomod.proxy` off for private module setups that cannot use `proxy.golang.org` and `sum.golang.org`; explain the tradeoff if you disable it.
- Treat provenance as a policy input, not a blanket security guarantee. Verification only helps if consumers or downstream automation actually enforce it.
