# Monorepo Configuration

Release Please supports manifest-driven monorepos where each releasable path has its own current version and optional strategy overrides.

## Basic Setup

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "packages": {
    "packages/core": {
      "release-type": "node",
      "component": "core"
    },
    "packages/cli": {
      "release-type": "node",
      "component": "cli"
    }
  }
}
```

```json
{
  "packages/core": "1.0.0",
  "packages/cli": "2.1.0"
}
```

Package keys must be directory paths relative to the repository root.

## Release PR Shape

### Combined PRs

Default manifest behavior:

```json
{
  "separate-pull-requests": false,
  "packages": {
    "packages/core": {},
    "packages/cli": {}
  }
}
```

### Separate PRs

Use separate PRs when packages have distinct ownership or release cadence:

```json
{
  "separate-pull-requests": true,
  "packages": {
    "packages/core": {},
    "packages/cli": {}
  }
}
```

## Component Naming

`component` affects tags, release names, and PR presentation:

```json
{
  "packages": {
    "packages/sdk": {
      "component": "sdk",
      "include-component-in-tag": true
    }
  }
}
```

## Current Plugin Set

These plugin names are current in the upstream schema:

| Plugin | Use |
|--------|-----|
| `node-workspace` | npm, pnpm, or Yarn workspaces |
| `cargo-workspace` | Rust workspaces |
| `maven-workspace` | Multi-module Maven repositories |
| `linked-versions` | Keep selected packages on the same version |
| `group-priority` | Control release grouping and order |
| `sentence-case` | Normalize changelog entry capitalization |

### Node Workspace Example

```json
{
  "plugins": [
    {
      "type": "node-workspace",
      "updateAllPackages": true
    }
  ],
  "packages": {
    "packages/core": {},
    "packages/cli": {},
    "packages/types": {}
  }
}
```

### Linked Versions Example

```json
{
  "plugins": [
    {
      "type": "linked-versions",
      "groupName": "platform",
      "components": ["packages/core", "packages/cli"]
    }
  ],
  "packages": {
    "packages/core": {},
    "packages/cli": {}
  }
}
```

### Group Priority Example

```json
{
  "plugins": [
    {
      "type": "group-priority",
      "groups": ["packages/core", "packages/cli"]
    }
  ]
}
```

## Root Package Plus Subpackages

If the repository root itself is also releasable:

```json
{
  "packages": {
    ".": {
      "release-type": "node",
      "component": "root"
    },
    "packages/core": {},
    "packages/cli": {}
  }
}
```

## Path-Based Detection

Release Please attributes commits to packages based on changed paths, not on the commit scope text alone. Scope text helps readability; changed files determine which package is considered updated.

### Excluding Paths

```json
{
  "packages": {
    "packages/core": {
      "exclude-paths": [
        "packages/core/test/",
        "packages/core/**/*.test.ts"
      ]
    }
  }
}
```

## GitHub Action Outputs

Monorepo outputs are prefixed by package path:

```yaml
jobs:
  release-please:
    runs-on: ubuntu-latest
    outputs:
      paths_released: ${{ steps.release.outputs.paths_released }}
      core_release_created: ${{ steps.release.outputs['packages/core--release_created'] }}
      core_version: ${{ steps.release.outputs['packages/core--version'] }}
    steps:
      # release-please-action v4.4.0
      - uses: googleapis/release-please-action@16a9c90856f42705d54a6fda1823352bdc62cf38
        id: release

  publish-core:
    needs: release-please
    if: ${{ needs.release-please.outputs.core_release_created == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - run: echo "Publish packages/core@${{ needs.release-please.outputs.core_version }}"
```

`paths_released` is a JSON array of package paths with releases on that run.

## Monorepo Recommendations

1. Start with combined release PRs unless ownership boundaries force separation.
2. Use `node-workspace`, `cargo-workspace`, or `maven-workspace` only when the workspace tool actually manages cross-package version relationships.
3. Keep publish jobs separate per package or package group, and gate each one on the corresponding `path--release_created` output.
4. Avoid relying on commit scopes alone to route releases.

## Canonical References

- https://github.com/googleapis/release-please/blob/main/docs/manifest-releaser.md
- https://github.com/googleapis/release-please/blob/main/schemas/config.json
- https://github.com/googleapis/release-please-action
