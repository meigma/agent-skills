# Configuration Notes

Assistant-facing notes for common Moon v2 config shapes. Keep this short and defer full
surface area to the live docs.

## Primary docs

- Workspace config: https://moonrepo.dev/docs/config/workspace
- Toolchains config: https://moonrepo.dev/docs/config/toolchain
- Project config: https://moonrepo.dev/docs/config/project
- Migration guide: https://moonrepo.dev/docs/migrate/2.0
- Root-level project guide: https://moonrepo.dev/docs/guides/root-project

## Grounded rules

1. A Moon workspace root is identified by `.moon/` or `.config/moon/`. `workspace.*` is required.
2. `projects` supports a map, a list of globs, or both via `globs` plus `sources`.
3. Use `defaultProject` only when a no-scope task target should resolve to one primary project.
4. Moon v2 uses `.moon/toolchains.*` (plural). Do not refer to `.moon/toolchain.*`.
5. `go` and `rust` are stable toolchain IDs in v2. Only Python remains `unstable_python`,
   `unstable_pip`, and `unstable_uv`.
6. `bun`, `deno`, and `node` require the `javascript` toolchain to also be enabled.
7. For root-level tasks, the docs recommend restricting `inputs` or setting `inputs: []`, and
   excluding inherited tasks with `workspace.inheritedTasks.include: []` if the root project
   should stay isolated.

## High-signal migration hazards

- Old codeowners auto-sync field -> `codeowners.sync`
- Old singular toolchains filename -> current plural `.moon/toolchains.*`
- Older unstable Go and Rust IDs -> stable `go` and `rust`
- Older project-type relationship key -> `constraints.enforceLayerRelationships`

If an old snippet still uses removed names, prefer rewriting it instead of translating it from
memory.

## Vetted examples

### Workspace with explicit and glob-discovered projects

```yaml
projects:
  globs:
    - 'apps/*'
    - 'packages/*'
  sources:
    root: '.'
    eslintConfig: 'tools/eslint-config'

defaultProject: 'web'
```

### Toolchains with current v2 identifiers

```yaml
javascript:
  packageManager: 'pnpm'

node:
  version: '24.0.0'

go:
  version: '1.24.0'

rust:
  version: '1.87.0'

unstable_python:
  version: '3.12.0'
  packageManager: 'uv'
```

### Root-level project with explicit caveats

```yaml
# .moon/workspace.yml
projects:
  root: '.'
```

```yaml
# /moon.yml
workspace:
  inheritedTasks:
    include: []

tasks:
  formatCheck:
    command: 'prettier --check .'
    inputs: []
    options:
      cache: false
```

## Use these notes for

- Choosing a safe starting shape for workspace, toolchains, and project config.
- Spotting old v1 or prerelease snippets quickly.
- Redirecting to the exact docs page instead of expanding this file into a full reference.
