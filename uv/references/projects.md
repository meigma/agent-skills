# uv Projects

Use this note when the task is about creating, modifying, or reasoning about a
Python project managed by `uv`. Keep the official docs open for exact CLI
surface area; this file is for defaults, structure, and footguns.

## Start with an explicit project shape

Default `uv init` is fine for a simple application, but be explicit when the
project type matters:

- `uv init <path>`: quick app-style project scaffold
- `uv init --app <path>`: make executable application intent explicit
- `uv init --lib <path>`: make library/package intent explicit
- `uv init --package <path>`: ask for a buildable package scaffold when package
  semantics matter
- `uv init --bare <path>`: only create `pyproject.toml`; use this when the repo
  layout already exists and you only need metadata bootstrapped

Prefer explicit flags over relying on defaults when the repository will be
shared or published.

## Understand the four files that matter

- `pyproject.toml`: broad project metadata, dependency declarations, and
  `tool.uv` configuration
- `.python-version`: the default Python version for the project environment
- `.venv`: the managed local environment; usually keep it local and ignored
- `uv.lock`: exact resolved dependency graph; commit it to version control and
  do not hand-edit it

`uv` creates `.venv` and `uv.lock` the first time a command such as `uv run`,
`uv sync`, or `uv lock` needs them.

## Preferred dependency workflow

Use `uv` commands for dependency changes unless you are making a broader manual
metadata edit:

```bash
uv add ruff
uv add --dev pytest
uv add --group docs mkdocs
uv add --optional cli rich
uv remove ruff
uv add -r requirements.txt
```

Good defaults:

- Use `uv add` and `uv remove` instead of hand-editing dependency arrays for
  ordinary changes.
- Use dependency groups and extras intentionally; do not dump everything into
  the default project dependencies.
- Prefer targeted upgrades when you want predictable lockfile churn:

```bash
uv lock --upgrade-package ruff
```

Use all-package upgrades only when you actually want the whole graph to move.

## Locking and syncing semantics

Projects are mostly automatic:

- `uv run ...`: checks that `uv.lock` matches project metadata, then syncs the
  environment before running
- `uv lock`: explicitly refreshes the lockfile
- `uv sync`: explicitly synchronize the environment

Use these flags deliberately:

- `--locked`: fail if the lockfile would need to change
- `--frozen`: use the lockfile without checking whether it is up to date
- `--no-sync`: skip environment synchronization

Useful checks:

```bash
uv lock --check
uv sync --check
```

For CI or reproducibility-sensitive flows, prefer explicit checks over assuming
the environment is current.

## Exact vs inexact environments

This trips people up:

- `uv sync` is exact by default, so it removes packages not present in the
  lockfile
- `uv run` is inexact by default, so it installs what is needed without
  removing extraneous packages

When you need `uv run` to clean extras too, opt in:

```bash
uv run --exact pytest
```

Use this distinction intentionally instead of treating `run` and `sync` as
interchangeable.

## Editor and shell hygiene

For routine work, prefer:

```bash
uv run pytest
uv run ruff check .
uv run python -m your_package
```

Use `uv sync` and `.venv` activation when:

- your editor needs a stable interpreter path
- you want an interactive shell with many repeated commands
- a tool insists on a pre-activated environment

Do not normalize "activate first, then remember to manage packages manually" as
the primary workflow. Let `uv run` and `uv sync` do the environment bookkeeping.

## Workspace guidance

Treat workspaces as a secondary tool, not the default starting point.

Use a workspace when:

- one repository contains multiple related packages
- those packages should share a single lockfile
- you want root-oriented commands with `--package` to target members

Remember:

- `uv lock` operates across the whole workspace
- `uv run` and `uv sync` default to the workspace root
- `uv run --package <member> ...` and `uv sync --package <member>` target a
  specific member

Prefer plain projects with path dependencies instead when:

- members need separate environments
- members have conflicting requirements
- you do not want one shared `requires-python` intersection

## Source map

- Project guide: https://docs.astral.sh/uv/guides/projects/
- Locking and syncing: https://docs.astral.sh/uv/concepts/projects/sync/
- Running commands: https://docs.astral.sh/uv/concepts/projects/run/
- Workspaces: https://docs.astral.sh/uv/concepts/projects/workspaces/
- `pyproject.toml`: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
