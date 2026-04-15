# Signing Releases with Cosign

Use this file when the release pipeline signs artifacts.

Sources:
- https://goreleaser.com/customization/sign/sign/
- https://goreleaser.com/blog/cosign-v3/
- https://docs.sigstore.dev/quickstart/quickstart-ci/
- local validation: `cosign sign-blob --help`, `cosign verify-blob --help`

## Default: keyless bundle signing of checksums

For new pipelines, default to Cosign keyless signing and sign the checksum file, not every archive or binary.

```yaml
signs:
  - cmd: cosign
    signature: "${artifact}.sigstore.json"
    args:
      - sign-blob
      - "--bundle=${signature}"
      - "${artifact}"
      - "--yes"
    artifacts: checksum
```

Why this is the default:

- one bundle file is easier to distribute than separate `.sig` and `.pem` files
- the checksum file already binds every shipped artifact digest
- downstream consumers can verify one signature and then verify file hashes locally

Do not add `COSIGN_EXPERIMENTAL=1`. Current Cosign v3 flows do not require it.

## GitHub Actions requirements

- grant `id-token: write`
- install Cosign explicitly in the workflow
- keep the verification identity precise enough to name the release workflow, not just the repository

Source references:
- https://docs.sigstore.dev/quickstart/quickstart-ci/
- https://goreleaser.com/ci/actions/

## Verification command

For a tagged GitHub Actions release, prefer an exact workflow identity:

```bash
cosign verify-blob \
  --bundle checksums.txt.sigstore.json \
  --certificate-identity "https://github.com/OWNER/REPO/.github/workflows/release.yml@refs/tags/v1.2.3" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  checksums.txt

sha256sum -c checksums.txt --ignore-missing
```

This is stronger than a repo-only regex because it binds verification to the specific release workflow and ref.

## Release notes snippet

If the release runs in GitHub Actions, include exact verification instructions in the release footer:

```yaml
release:
  footer: |
    ## Verification

    ```bash
    cosign verify-blob \
      --bundle checksums.txt.sigstore.json \
      --certificate-identity "https://github.com/{{ .Env.GITHUB_REPOSITORY }}/.github/workflows/release.yml@refs/tags/{{ .Tag }}" \
      --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
      checksums.txt
    sha256sum -c checksums.txt --ignore-missing
    ```
```

## When to sign more than checksums

Use `artifacts: archive`, `artifacts: binary`, or `artifacts: all` only when the consumer workflow truly needs per-artifact detached signatures.

Good reasons:

- a downstream distribution channel expects detached signatures next to each archive
- consumers verify individual files without consulting the checksum manifest
- policy requires a signature on every distributable object

Otherwise, keep `artifacts: checksum`.

## Non-OIDC fallback

If the environment cannot mint OIDC tokens, use a managed key or private key only as a fallback. Call out the added secret-management burden and log-handling risk before recommending it.
