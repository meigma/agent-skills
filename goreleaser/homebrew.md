# Homebrew Publishing

Use this file only when Homebrew publishing is in scope.

Sources:
- https://goreleaser.com/customization/publish/homebrew_casks/
- https://www.goreleaser.com/customization/publish/homebrew_formulas/
- local validation: `goreleaser jsonschema`, `goreleaser check`

## Default to Homebrew casks

Use `homebrew_casks` for new Homebrew publishing work. GoReleaser marks `brews` formulas as deprecated since v2.10.

Minimal cask config:

```yaml
homebrew_casks:
  - name: myapp
    ids:
      - myapp
    repository:
      owner: myorg
      name: homebrew-tap
      branch: main
      token: "{{ .Env.HOMEBREW_TAP_TOKEN }}"
    homepage: "https://github.com/myorg/myapp"
    description: "My application"
    license: "MIT"
    binaries:
      - myapp
```

Use a dedicated token only for the tap repository. For cross-repo publishing, prefer:

- a GitHub App token, or
- a fine-grained PAT scoped to the tap repository

Use a classic PAT with broad `repo` access only as a legacy fallback and call out the broader risk explicitly.

## Pull request flow for the tap

If the tap should update by pull request rather than direct push:

```yaml
homebrew_casks:
  - name: myapp
    repository:
      owner: myorg
      name: homebrew-tap
      branch: main
      token: "{{ .Env.HOMEBREW_TAP_TOKEN }}"
      pull_request:
        enabled: true
        draft: false
        base:
          owner: myorg
          name: homebrew-tap
          branch: main
    homepage: "https://github.com/myorg/myapp"
    description: "My application"
    license: "MIT"
    binaries:
      - myapp
```

## Private repositories

GoReleaser documents private-repo cask support using custom URLs, headers, and custom Homebrew Ruby blocks. Treat that as an advanced edge case, not the default. It relies on Homebrew internals and should only be used when the repository must remain private.

Source: https://goreleaser.com/customization/publish/homebrew_casks/

## Legacy formulas note

`brews` formulas are deprecated. Keep them only when you already have formula consumers you cannot migrate yet. Do not present `brews` as the default path in new skills, templates, or review guidance.
