# GitHub Actions Notes

Assistant-facing notes for Moon CI usage on GitHub Actions.

## Primary docs

- `moon ci`: https://moonrepo.dev/docs/commands/ci
- `moon check`: https://moonrepo.dev/docs/commands/check
- `moon run`: https://moonrepo.dev/docs/commands/run
- Official examples workflow:
  https://github.com/moonrepo/examples/blob/b38838408ab50c9af6647a252f06d761b3a5a4f2/.github/workflows/ci.yml
- Migration guide CI behavior:
  https://moonrepo.dev/docs/migrate/2.0

## Grounded rules

1. Use `actions/checkout@v4` with `fetch-depth: 0`. Moon change detection depends on git history.
2. Start with `moon ci` for pull-request and push validation. In v2 it runs affected tasks that
   have `runInCI` enabled.
3. `moon check` is a different command that runs build and test related tasks for one or many
   projects. Use it intentionally; do not treat it as a drop-in replacement for `moon ci`.
4. Use `moonrepo/setup-toolchain@v0` when following the official Moon example workflow.
5. Sharding uses `--job` and `--job-total`. Prefer the exact flag spelling from local CLI help.
6. `moon ci`, `moon check`, `moon run`, and `moon exec` all respect `runInCI` semantics in v2
   when in CI mode.

## Vetted examples

### Minimal CI job

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: moonrepo/setup-toolchain@v0
      - run: moon ci
      - uses: moonrepo/run-report-action@v1
        if: success() || failure()
        with:
          access-token: ${{ secrets.GITHUB_TOKEN }}
```

### Sharded CI

```yaml
strategy:
  matrix:
    index: [0, 1, 2, 3]

steps:
  - uses: actions/checkout@v4
    with:
      fetch-depth: 0
  - uses: moonrepo/setup-toolchain@v0
  - run: moon ci --job ${{ matrix.index }} --job-total 4
```

## Notes for assistants

- Validate flags against `moon ci --help` before suggesting them.
- Keep CI examples minimal unless the repo already uses custom caching or report formatting.
- If you need "run everything" semantics, say so explicitly and consider `moon check --all` or
  explicit `moon run :task` targets rather than implying that `moon ci` always runs the full graph.
