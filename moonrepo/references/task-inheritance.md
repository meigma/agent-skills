# Task Inheritance Notes

Assistant-facing notes for the task inheritance model in Moon v2.

## Primary docs

- Task inheritance: https://moonrepo.dev/docs/concepts/task-inheritance
- Targets: https://moonrepo.dev/docs/concepts/target
- Create a task: https://moonrepo.dev/docs/create-task
- `.moon/tasks` config file: https://moonrepo.dev/docs/config/tasks

## Grounded rules

1. Workspace-level tasks live in `.moon/tasks/**/*` and can be inherited by many projects.
2. `inheritedBy` controls which projects inherit a global task file. Supported conditions include
   file(s), language(s), layer(s), stack(s), tag(s), and toolchain(s).
3. Multiple `inheritedBy` conditions are combined with AND semantics.
4. `tags` and `toolchains` support `and`, `or`, and `not` clauses for more precise matching.
5. When a global task and a local task share the same name, Moon merges them using
   `merge`, `mergeArgs`, `mergeDeps`, `mergeEnv`, `mergeInputs`, `mergeOutputs`, and
   `mergeToolchains`.
6. Projects can include, exclude, or rename inherited tasks with `workspace.inheritedTasks`
   in project `moon.*`.

## Vetted examples

### Inherit a build task for frontend libraries

```yaml
inheritedBy:
  toolchain: 'node'
  stack: 'frontend'
  layer: 'library'

tasks:
  build:
    command: 'vite build'
    outputs: ['dist/']
```

### Use clauses for tags or toolchains

```yaml
inheritedBy:
  toolchains:
    or: ['node', 'deno']
  tags:
    not: ['legacy']
  layer: 'library'
```

### Override merge behavior locally

```yaml
tasks:
  build:
    args: '--no-color --no-stats'
    deps:
      - 'designSystem:build'
    options:
      mergeArgs: 'append'
      mergeDeps: 'prepend'
```

## Notes for assistants

- Reach for inheritance when many projects genuinely share task shape.
- Keep the first pass simple; add merge overrides only after reading the effective local task.
- Use exact target syntax from the docs: `project:task`, `:task`, `'#tag:task'`, `'~:task'`,
  and `^:task` where appropriate.
