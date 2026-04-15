# Configuration Reference

Use this file when writing or reviewing `.goreleaser.yaml`.

Sources:
- https://goreleaser.com/customization/
- https://goreleaser.com/customization/builds/verifiable_builds/
- https://goreleaser.com/customization/release/
- https://goreleaser.com/customization/sign/sign/
- https://goreleaser.com/customization/sbom/
- local validation: `goreleaser jsonschema`, `goreleaser check`

## File setup

```yaml
# yaml-language-server: $schema=https://goreleaser.com/static/schema.json
version: 2
```

Keep complete examples valid under the current schema. `goreleaser check` rejects stale keys such as `rlcp_files` and rejects a top-level `after:` block.

## Baseline secure config

This example validates with `goreleaser 2.14.3`:

```yaml
# yaml-language-server: $schema=https://goreleaser.com/static/schema.json
version: 2

project_name: myapp

before:
  hooks:
    - go test ./...

gomod:
  proxy: true
  env:
    - GOPROXY=https://proxy.golang.org,direct
    - GOSUMDB=sum.golang.org

builds:
  - id: myapp
    main: ./cmd/myapp
    binary: myapp
    flags:
      - -trimpath
    ldflags:
      - -X main.version={{ .Version }}
      - -X main.commit={{ .FullCommit }}
      - -X main.date={{ .Date }}
    goos:
      - linux
      - darwin
      - windows
    goarch:
      - amd64
      - arm64
    ignore:
      - goos: windows
        goarch: arm64

archives:
  - id: default
    ids:
      - myapp
    formats:
      - tar.gz
    format_overrides:
      - goos: windows
        formats:
          - zip
    files:
      - LICENSE*
      - README*

checksum:
  name_template: checksums.txt

release:
  draft: false
  prerelease: auto
  mode: keep-existing

signs:
  - cmd: cosign
    signature: "${artifact}.sigstore.json"
    args:
      - sign-blob
      - "--bundle=${signature}"
      - "${artifact}"
      - "--yes"
    artifacts: checksum

sboms:
  - artifacts: archive
```

Sources:
- https://goreleaser.com/customization/builds/verifiable_builds/
- https://goreleaser.com/customization/package/archives/
- https://goreleaser.com/customization/publish/scm/
- https://goreleaser.com/customization/sign/sign/
- https://goreleaser.com/customization/sbom/

## Current config rules

- Use `formats`, not the deprecated singular `format`, for new archive configs.
- Use `files` to include extra archive contents. There is no valid `rlcp_files` key in current GoReleaser.
- Use top-level `before.hooks` for preflight commands. There is no top-level `after` section in current GoReleaser.
- Use `builds[].hooks.pre` and `builds[].hooks.post` only when you actually need per-build commands.
- Use `release.mode: keep-existing` unless you explicitly want `append`, `prepend`, or `replace`.
- Prefer `homebrew_casks` for Homebrew publishing. `brews` formulas are deprecated.
- Prefer `.FullCommit` over `.Commit` in new templates.

## Useful partial patterns

Per-build hooks:

```yaml
builds:
  - id: myapp
    main: ./cmd/myapp
    hooks:
      pre: go generate ./...
      post: ./scripts/post-build.sh {{ .Path }}
```

Use an existing GitHub draft release:

```yaml
release:
  draft: true
  use_existing_draft: true
  replace_existing_draft: true
```

Snapshot naming:

```yaml
snapshot:
  version_template: "{{ .Tag }}-next-{{ .ShortCommit }}"
```

Source references:
- https://goreleaser.com/customization/build/
- https://goreleaser.com/customization/release/
- https://goreleaser.com/customization/snapshots/

## Validation commands

```bash
goreleaser check
goreleaser jsonschema
```

If a snippet is intended to be complete, validate it before handing it to the user.
