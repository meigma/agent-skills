# Monorepo Pattern Notes

Assistant-facing guidance for structuring a Moon workspace without inventing extra policy.

## Primary docs

- Create a project: https://moonrepo.dev/docs/create-project
- Workspace config: https://moonrepo.dev/docs/config/workspace
- Project graph: https://moonrepo.dev/docs/commands/project-graph
- Root-level project: https://moonrepo.dev/docs/guides/root-project
- Introduction and support matrix: https://moonrepo.dev/docs

## Grounded rules

1. Keep project discovery simple: use a manual map for explicit IDs, globs for scale, or
   `globs` plus `sources` when you need both.
2. If glob-discovered IDs are likely to collide, use `projects.globFormat: 'source-path'`.
3. Let Moon infer relationships from supported manifests when it can. Use `dependsOn` for
   cross-ecosystem or non-manifest relationships.
4. Treat `language`, `layer`, `stack`, and `tags` as useful metadata, not mandatory boilerplate.
   Add them when they drive inheritance, constraints, or workspace clarity.
5. Reach for `constraints.enforceLayerRelationships` and `constraints.tagRelationships` only
   once project metadata and dependency edges are already trustworthy.
6. Use a root-level project intentionally for repository-wide maintenance tasks, not as the
   default place for every command.
7. Workspace-level CODEOWNERS sync uses `codeowners.sync` in v2.

## Vetted examples

### Mixed explicit and glob project discovery

```yaml
projects:
  globFormat: 'source-path'
  globs:
    - 'apps/*'
    - 'packages/*'
    - 'services/**/moon.yml'
  sources:
    root: '.'
    eslintConfig: 'tools/eslint-config'
```

### Explicit cross-ecosystem dependency

```yaml
dependsOn:
  - id: 'api-clients'
    scope: 'production'
```

### Root-level maintenance task

```yaml
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

## Useful inspection commands

```bash
moon projects --json
moon project-graph
moon project-graph web
moon action-graph :build
```

## Notes for assistants

- Prefer documented defaults over forcing a house style.
- When suggesting structure, explain what Moon feature the metadata unlocks
  instead of requiring every project to carry all classification fields.
- If no official page backs a structural recommendation, present it as optional.
