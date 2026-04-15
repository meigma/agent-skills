# GitHub Actions Integration

Use this file when the release should run in GitHub Actions.

Sources:
- https://goreleaser.com/ci/actions/
- https://goreleaser.com/customization/attestations/
- https://docs.github.com/en/actions/reference/security/secure-use
- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
- live release metadata from GitHub for pinned SHAs, checked on April 10, 2026

## Pinned actions used below

These SHAs were resolved from the current release tags on April 10, 2026:

- `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd` (`v6.0.2`)
- `actions/setup-go@4a3601121dd01d1626a1e23e37211e3254c1c06c` (`v6.4.0`)
- `goreleaser/goreleaser-action@ec59f474b9834571250b370d4735c50f8e2d1e29` (`v7.0.0`)
- `anchore/sbom-action/download-syft@e22c389904149dbc22b58101806040fa8d37a610` (`v0.24.0`)
- `sigstore/cosign-installer@cad07c2e89fa2edd6e2d7bab4c1aa38e53f76003` (`v4.1.1`)
- `actions/attest@59d89421af93a897026c735860bf21b6eb4f7b26` (`v4.1.0`)

## Secure tag release workflow

```yaml
name: release

on:
  push:
    tags:
      - "v*"

permissions:
  contents: write
  id-token: write
  attestations: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
        with:
          fetch-depth: 0
          persist-credentials: false

      - name: Set up Go
        uses: actions/setup-go@4a3601121dd01d1626a1e23e37211e3254c1c06c # v6.4.0
        with:
          go-version-file: go.mod
          cache: true

      - name: Install Syft
        uses: anchore/sbom-action/download-syft@e22c389904149dbc22b58101806040fa8d37a610 # v0.24.0

      - name: Install Cosign
        uses: sigstore/cosign-installer@cad07c2e89fa2edd6e2d7bab4c1aa38e53f76003 # v4.1.1
        with:
          cosign-release: v3.0.5

      - name: Run GoReleaser
        id: goreleaser
        uses: goreleaser/goreleaser-action@ec59f474b9834571250b370d4735c50f8e2d1e29 # v7.0.0
        with:
          distribution: goreleaser
          version: v2.14.3
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Attest released files listed in checksums.txt
        uses: actions/attest@59d89421af93a897026c735860bf21b6eb4f7b26 # v4.1.0
        with:
          subject-checksums: ./dist/checksums.txt
```

This workflow matches the current GoReleaser guidance that the action does not install dependencies for you. Syft and Cosign must be installed explicitly.

## Snapshot workflow for PRs

```yaml
name: snapshot

on:
  pull_request:

permissions:
  contents: read

jobs:
  snapshot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
        with:
          fetch-depth: 0
          persist-credentials: false

      - uses: actions/setup-go@4a3601121dd01d1626a1e23e37211e3254c1c06c # v6.4.0
        with:
          go-version-file: go.mod
          cache: true

      - uses: goreleaser/goreleaser-action@ec59f474b9834571250b370d4735c50f8e2d1e29 # v7.0.0
        with:
          distribution: goreleaser
          version: v2.14.3
          args: release --snapshot --clean
```

## Permissions and token guidance

- `contents: write` only if the workflow creates releases or uploads release assets.
- `packages: write` only if the workflow pushes container images.
- `id-token: write` only if the workflow uses keyless Cosign or GitHub artifact attestations.
- `attestations: write` only if the workflow generates GitHub artifact attestations.

Token defaults:

- Same-repo releases: use `secrets.GITHUB_TOKEN`.
- Cross-repo publishing, such as a separate Homebrew tap: prefer a GitHub App token or a fine-grained PAT scoped to the target repository.
- Classic PATs with `repo` scope are a legacy fallback only. Call out the broader blast radius if the user asks for them.

Source references:
- GoReleaser token guidance: https://goreleaser.com/ci/actions/
- GitHub least-privilege and full-SHA guidance: https://docs.github.com/en/actions/reference/security/secure-use
- GitHub token guidance: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

## Workflow hardening rules

- Protect `.github/workflows/` with `CODEOWNERS`.
- Audit the source of every third-party action before changing a pin.
- Keep `fetch-depth: 0` for GoReleaser jobs so changelog generation and tag discovery work correctly.
- Do not use `latest` or moving major tags as the only pin. Keep the release tag in a comment, but pin the actual step to a full SHA.
- If the release also publishes container images, add `packages: write` and a second `actions/attest` step for `./dist/digests.txt`.
