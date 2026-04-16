---
name: uv
description: >
  Use when creating or maintaining Python projects with Astral's `uv`, or when
  authoring and running self-contained Python scripts with inline metadata and a
  `uv` shebang. Covers `uv init`, `uv add`, `uv run`, `uv sync`, `uv lock`,
  `uv.lock`, `.python-version`, `pyproject.toml`, PEP 723 inline script
  metadata, and executable shebang scripts.
---

# uv

Use this skill as a current operator guide for Astral's `uv`. Prefer official
`uv` docs, packaging specs, and the local `uv --help` output over memory or
older blog posts.

## Verified against

- Astral docs pages listed below, accessed on 2026-04-15
- Local CLI used for command grounding: `uv 0.11.0`

## Use this skill when

- You are starting or maintaining a Python project managed by `uv`.
- You need to decide between a full `uv` project and a single self-contained
  script.
- You are editing or explaining `pyproject.toml`, `.python-version`, `.venv`,
  or `uv.lock`.
- You are authoring standalone scripts with inline metadata and an executable
  `uv` shebang.

## Choose the shape first

1. Use a project when the codebase has multiple modules, tests, editor
   integration needs, packaging concerns, or shared team workflows.
2. Use a self-contained script when the unit of work is a single file that
   should carry its own interpreter and dependency metadata.
3. Reach for workspaces only when multiple packages need one shared lockfile and
   one shared dependency graph. Otherwise prefer normal projects with path
   dependencies.

## Working rules

1. Prefer native `uv` flows: `uv init`, `uv add`, `uv remove`, `uv run`,
   `uv sync`, and `uv lock`. Treat `uv pip` as a compatibility escape hatch,
   not the default interface.
2. Treat `uv.lock` as generated state. Commit it for projects, but do not edit
   it by hand.
3. In a project, `uv run` includes the project by default. Put `--no-project`
   before the script path when you want to skip project discovery. If you also
   need a clean ephemeral environment, use inline metadata or combine
   `--isolated` with `--no-project`.
4. Scripts with inline metadata run in an isolated script environment, even when
   they live inside a `uv` project.
5. Projects auto-lock and auto-sync on `uv run`. Scripts do not get persistent
   lockfiles unless you explicitly run `uv lock --script`.
6. Prefer `uv run <command>` over activating `.venv` for routine commands. Use
   activation only when the shell session or editor needs a persistent
   environment.

## Local notes

- Project workflow notes: [references/projects.md](references/projects.md)
- Script workflow notes: [references/scripts.md](references/scripts.md)

## Authoritative sources

- https://docs.astral.sh/uv/guides/projects/
- https://docs.astral.sh/uv/concepts/projects/sync/
- https://docs.astral.sh/uv/concepts/projects/run/
- https://docs.astral.sh/uv/guides/scripts/
- https://docs.astral.sh/uv/concepts/projects/workspaces/
- https://docs.astral.sh/uv/reference/cli/
- https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- https://packaging.python.org/en/latest/specifications/inline-script-metadata/

If the local CLI and the docs disagree, trust the local CLI for flag names and
trust the official docs for workflow intent. Re-check both before repeating a
version-sensitive claim.
