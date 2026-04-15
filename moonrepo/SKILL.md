---
name: moonrepo
description: >
  Configure, inspect, migrate, and automate monorepos with moon v2. Use when:
  (1) setting up or reviewing a moon workspace in `.moon/` or `.config/moon/`,
  (2) editing `.moon/workspace.*`, `.moon/toolchains.*`, `.moon/tasks/*`, or project `moon.*`,
  (3) configuring CI with `moon ci`, `moon check`, `moon run`, or `moonx`,
  (4) working with `defaultProject`, task inheritance, `moon extension`, or `moon docker file`,
  (5) grounding Moon guidance in live docs and the local CLI. Triggers on: moon, moonrepo,
  `.moon/toolchains`, `.config/moon`, `defaultProject`, `moon ci`, `moon check`, `moon run`,
  `moon extension`, `moon docker file`, `moonx`, proto.
---

# moonrepo

Use this skill as a v2-first operator guide. Prefer official Moon docs, the v2 migration guide,
the local CLI help, and official Moon examples over memory or older copied snippets.

## Verified against

- Docs: https://moonrepo.dev/docs
- Migration guide: https://moonrepo.dev/docs/migrate/2.0
- Official examples workflow:
  https://github.com/moonrepo/examples/blob/b38838408ab50c9af6647a252f06d761b3a5a4f2/.github/workflows/ci.yml
- Local CLI used for command grounding: `moon 2.1.3`

## Use this skill when

- A repository already uses Moon and you need to inspect, explain, or extend it safely.
- You are creating or editing `.moon/workspace.*`, `.moon/toolchains.*`, `.moon/tasks/*`, or
  project-level `moon.*`.
- You are migrating stale Moon guidance to v2 terminology and flags.
- You need CI or Docker guidance that matches current Moon commands.

## Working rules

1. Detect the workspace root first. Moon v2 supports either `.moon/` or `.config/moon/`.
2. Read the existing config before proposing structure changes. Do not overwrite local patterns
   unless the docs require a migration.
3. Ground command examples in the local CLI help. Keep quoted targets like `'#frontend:lint'`
   and `'~:test'`.
4. Prefer current v2 terminology and identifiers:
   - `.moon/toolchains.*` is plural.
   - `go` and `rust` are stable toolchain IDs.
   - Only Python remains `unstable_*`.
   - `bun`, `deno`, and `node` require `javascript`.
   - `moon docker file <project>` is the primary Docker entrypoint to recommend.
5. If a claim cannot be grounded in official docs, local CLI help, or official Moon examples,
   remove it instead of guessing.

## Fast inspection workflow

Use these commands before giving advice:

```bash
moon --version
moon --help
moon projects --json
moon project <id>
moon tasks [project]
moon task <target>
moon run --help
moon ci --help
moon docker --help
moon extension --help
moon toolchain info node
```

Useful workspace checks:

```bash
rg --files -g 'workspace.*' -g 'toolchains.*' -g 'moon.*' .moon .config/moon
rg -n "defaultProject|tagRelationships|enforceLayerRelationships|runInCI" .moon .config/moon
```

## Safe guidance to prefer

- Project discovery:
  use a manual map for explicit IDs, glob lists for scale, or `globs` plus `sources` when both
  are needed.
- Root-level project:
  add `root: '.'` (or `projects: ['.']`), define a root `moon.*`, and usually restrict
  `inputs` or set `inputs: []`. Exclude inherited tasks with
  `workspace.inheritedTasks.include: []` when the root should not inherit global tasks.
- CI:
  start with `moon ci`, `actions/checkout@v4`, and `fetch-depth: 0`. Use the kebab-case
  sharding flags from current `moon ci --help`.
- Docker:
  prefer `moon docker file <project>` and current generated structure under
  `.moon/docker/configs` and `.moon/docker/sources`.
- Task inheritance:
  use `.moon/tasks/**/*` and `inheritedBy` when it reduces duplication; use local task merge
  options only when the inherited shape really needs adjustment.

## Curated notes

- [Configuration](references/configuration.md)
- [Language support](references/language-support.md)
- [GitHub Actions](references/github-actions.md)
- [Task inheritance](references/task-inheritance.md)
- [Monorepo patterns](references/monorepo-patterns.md)

These are assistant-facing notes, not copied source-of-truth references.

## Maintenance checklist

Re-verify this skill when Moon releases a new minor or major version:

1. Re-open these docs:
   - https://moonrepo.dev/docs
   - https://moonrepo.dev/docs/migrate/2.0
   - https://moonrepo.dev/docs/commands/run
   - https://moonrepo.dev/docs/commands/ci
   - https://moonrepo.dev/docs/commands/docker/file
   - https://moonrepo.dev/docs/config/workspace
   - https://moonrepo.dev/docs/config/toolchain
   - https://moonrepo.dev/docs/config/project
2. Re-run these commands locally:
   - `moon --help`
   - `moon run --help`
   - `moon ci --help`
   - `moon docker --help`
   - `moon extension --help`
   - `moon toolchain info go`
   - `moon toolchain info rust`
   - `moon toolchain info unstable_python`
3. Smoke test in a temp directory:
   - `moon init --minimal --yes`
   - optional: `moon docker file <project> --defaults`
4. Delete any recommendation that can no longer be grounded.
