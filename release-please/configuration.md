# Configuration Reference

Release Please manifest mode uses two repository files:

| File | Purpose |
|------|---------|
| `release-please-config.json` | Release behavior and package configuration |
| `.release-please-manifest.json` | Current released versions by path |

## Minimal Configuration

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "release-type": "node",
  "packages": {
    ".": {}
  }
}
```

```json
{
  ".": "1.0.0"
}
```

## High-Value Top-Level Options

These are the options most likely to matter in real repositories:

| Option | Meaning |
|--------|---------|
| `release-type` | Default strategy for packages that do not override it |
| `bootstrap-sha` | First-run cutoff for changelog history |
| `last-release-sha` | Manual override for the previous release marker |
| `plugins` | Workspace or release-group plugins |
| `bump-minor-pre-major` | For `<1.0.0`, make breaking changes bump minor instead of major |
| `bump-patch-for-minor-pre-major` | For `<1.0.0`, make features bump patch instead of minor |
| `versioning` | Versioning strategy such as `default` or `prerelease` |
| `prerelease-type` | Label such as `alpha` or `beta` for prerelease strategy |
| `prerelease` | Mark GitHub releases as prereleases when applicable |
| `force-tag-creation` | Create tags immediately, especially important with draft releases |
| `draft` | Create GitHub releases as drafts |
| `skip-github-release` | Skip GitHub release creation |
| `skip-changelog` | Skip changelog updates |
| `separate-pull-requests` | Split manifest releases into one PR per package |
| `always-update` | Update release PRs even when only branch state changed |
| `release-search-depth` | Limit how far back to search releases |
| `commit-search-depth` | Limit how far back to search commits |
| `commit-batch-size` | Control commit pagination batch size |
| `sequential-calls` | Reduce concurrency to avoid throttling in large repos |

## Common Package-Level Options

Each entry in `packages` can override top-level defaults:

```json
{
  "release-type": "node",
  "packages": {
    ".": {
      "component": "root",
      "include-v-in-tag": true,
      "changelog-path": "CHANGELOG.md"
    },
    "packages/cli": {
      "release-type": "node",
      "component": "cli",
      "include-component-in-tag": true
    }
  }
}
```

Package-level options you will commonly use:

| Option | Meaning |
|--------|---------|
| `release-type` | Package-specific strategy override |
| `package-name` | Required for some non-node strategies |
| `component` | Name used in tags and PR titles |
| `include-component-in-tag` | Include the component in the release tag |
| `include-v-in-tag` | Include `v` in the release tag |
| `changelog-path` | Package-specific changelog path |
| `exclude-paths` | Ignore changes from specific paths |
| `extra-files` | Update extra version-bearing files |

## Recommended Single-Package Config

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "release-type": "node",
  "packages": {
    ".": {}
  },
  "changelog-sections": [
    {"type": "feat", "section": "Features"},
    {"type": "fix", "section": "Bug Fixes"},
    {"type": "perf", "section": "Performance"},
    {"type": "revert", "section": "Reverts"},
    {"type": "docs", "section": "Documentation", "hidden": true},
    {"type": "chore", "section": "Maintenance", "hidden": true}
  ]
}
```

## Draft Releases with Immediate Tags

If you use draft GitHub releases, pair them with `force-tag-creation` so Release Please can still find the previous tag on the next run:

```json
{
  "release-type": "node",
  "draft": true,
  "force-tag-creation": true,
  "packages": {
    ".": {}
  }
}
```

## Prerelease Strategy

Use `versioning: "prerelease"` when you want prerelease increments such as `1.2.0-beta.1`:

```json
{
  "release-type": "node",
  "versioning": "prerelease",
  "prerelease": true,
  "prerelease-type": "beta",
  "packages": {
    ".": {}
  }
}
```

## Extra Files

Release Please supports these `extra-files` forms in the current schema:

### Generic Files with Inline Annotations

```json
{
  "extra-files": [
    "version.txt",
    {
      "type": "generic",
      "path": "src/version.txt"
    }
  ]
}
```

### JSON, YAML, and TOML via `jsonpath`

```json
{
  "extra-files": [
    {
      "type": "json",
      "path": "package.json",
      "jsonpath": "$.version"
    },
    {
      "type": "yaml",
      "path": "chart/Chart.yaml",
      "jsonpath": "$.appVersion"
    },
    {
      "type": "toml",
      "path": "pyproject.toml",
      "jsonpath": "$.tool.poetry.version"
    }
  ]
}
```

### XML via `xpath`

```json
{
  "extra-files": [
    {
      "type": "xml",
      "path": "pom.xml",
      "xpath": "//project/version"
    }
  ]
}
```

### Generic Inline Annotation Example

```python
# x-release-please-version
__version__ = "1.0.0"
```

## Bootstrapping and Initial Versions

Two common first-run tasks:

1. Set `bootstrap-sha` if you want the first changelog to start after a specific commit.
2. Set the current released version in `.release-please-manifest.json` so the first PR proposes the next correct version.

```json
{
  ".": "2.3.4"
}
```

## Deprecated or Use-Sparingly Options

- `release-as` in config is deprecated upstream; prefer a `Release-As:` footer in a commit body.
- `skip-github-release` is only correct if some other trusted mechanism creates and tags releases.
- `always-update` can increase API usage in large repos.

## Canonical References

- https://github.com/googleapis/release-please/blob/main/docs/manifest-releaser.md
- https://github.com/googleapis/release-please/blob/main/docs/customizing.md
- https://github.com/googleapis/release-please/blob/main/schemas/config.json
- https://github.com/googleapis/release-please-action
