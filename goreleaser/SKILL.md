---
name: releasing-go-binaries
description: Automates Go binary releases with GoReleaser. Use when publishing Go binaries, creating GitHub releases, signing checksums with Cosign v3 bundles, generating SBOMs, enabling verifiable builds, adding GitHub artifact attestations, or publishing Homebrew casks.
---

# Releasing Go Binaries with GoReleaser

Validated against April 10, 2026 with `goreleaser 2.14.3`, `cosign 3.0.5`, and `gh 2.88.1`.

Primary sources:
- https://goreleaser.com/cmd/goreleaser/
- https://goreleaser.com/ci/actions/
- https://goreleaser.com/customization/release/
- https://goreleaser.com/customization/builds/verifiable_builds/
- https://goreleaser.com/customization/sbom/
- https://goreleaser.com/customization/sign/sign/
- https://goreleaser.com/customization/publish/homebrew_casks/
- https://goreleaser.com/customization/attestations/
- https://docs.github.com/en/actions/reference/security/secure-use
- https://docs.sigstore.dev/quickstart/quickstart-ci/

Use this skill when the user wants a GoReleaser-based release pipeline or needs an existing one brought up to current supply-chain expectations.

Read these files as needed:
- [configuration.md](configuration.md) for valid GoReleaser config patterns and a baseline config that validates with the current schema.
- [github-actions.md](github-actions.md) for pinned GitHub Actions workflows, permissions, and token guidance.
- [signing.md](signing.md) for Cosign v3 bundle signing and exact verification commands.
- [sboms.md](sboms.md) for SBOMs, verifiable builds, and GitHub artifact attestations.
- [homebrew.md](homebrew.md) only when Homebrew publishing is in scope. Default to `homebrew_casks`. Treat `brews` formulas as legacy.

## Default secure workflow

1. Confirm the project releases from a clean Git state and a SemVer tag.
2. Run `goreleaser healthcheck` and `goreleaser check` before attempting a release.
3. Run `goreleaser release --snapshot --clean` locally or in PR CI to catch config problems before a tag.
4. For tagged releases in GitHub Actions, pin every third-party action to a full commit SHA and grant only the permissions the job needs.
5. Sign the checksum file with Cosign keyless signing, generate SBOMs, enable GoReleaser verifiable builds with `gomod.proxy`, and attest released artifacts from `checksums.txt`.
6. Prefer same-repo publishing with `GITHUB_TOKEN`. For cross-repo writes, prefer a GitHub App or a fine-grained PAT scoped to the target repository. Use classic `repo` PATs only as a legacy fallback.
7. Publish Homebrew only if required. Default to `homebrew_casks`; keep `brews` only for existing legacy consumers.

## Essential commands

```bash
# Initialize a starter config
goreleaser init

# Validate config syntax and schema
goreleaser check

# Verify external tools in PATH
goreleaser healthcheck

# Local dry run without publishing
goreleaser release --snapshot --clean

# Tagged release
goreleaser release --clean
```

Command sources:
- https://goreleaser.com/cmd/goreleaser/
- local validation: `goreleaser --help`, `goreleaser check --help`, `goreleaser healthcheck --help`, `goreleaser release --help`

## Security defaults

- Pin third-party GitHub Actions to full 40-character commit SHAs, not moving tags.
- Set the default `GITHUB_TOKEN` permissions to the minimum required by the job.
- Use Cosign keyless signing with `--bundle`; do not use `COSIGN_EXPERIMENTAL`.
- Sign the checksum file by default. Sign every archive or binary only when downstream verification requires detached signatures per artifact.
- Enable `gomod.proxy` for tagged releases that need verifiable builds.
- Generate SBOMs for shipped archives.
- Add GitHub artifact attestations for released files from `checksums.txt`, and for `digests.txt` if the release also publishes container images.
- Avoid unverified `curl | sh` installers in both docs and CI examples.
- Protect `.github/workflows/` with `CODEOWNERS` and review action source before changing pinned SHAs.

## Working rules for agents

- Do not invent GoReleaser keys. If a snippet is meant to be complete, validate it with `goreleaser check`.
- Prefer official GoReleaser docs, current CLI help, and the JSON schema over blog posts or copied snippets.
- Prefer exact verification identity for Cosign and precise signer workflow constraints for `gh attestation verify`.
- Do not recommend blanket `CGO_ENABLED=0`. Use it only when the binary is pure Go and portability matters more than CGO features.
