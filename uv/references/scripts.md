# uv Scripts

Use this note for single-file Python workflows: ad hoc automation, checked-in
utility scripts, or executable helpers that should carry their own dependency
metadata.

## Start with inline metadata

Use `uv` to scaffold the file instead of hand-writing the metadata block:

```bash
uv init --script script.py --python 3.12
```

Then add dependencies through `uv` so the metadata stays valid:

```bash
uv add --script script.py httpx rich
```

For one-off runs where you do not want to edit the script, `uv run --with ...`
is the short-lived escape hatch:

```bash
uv run --with rich script.py
```

Prefer inline metadata over repeated `--with` flags once the script becomes a
kept artifact.

## Inline metadata expectations

`uv` follows the standardized inline script metadata format. Keep the block at
the top of the file and let `uv` manage it when possible.

Important details:

- include `dependencies = []` even when the script currently has no third-party
  dependencies
- use `requires-python` when the script depends on a specific interpreter floor
- if the script has inline metadata, `uv run script.py` ignores project
  dependencies automatically

Minimal pattern:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

print("hello")
```

## Canonical shebang form

For executable scripts, use the shebang Astral documents:

```python
#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx"]
# ///

import httpx

print(httpx.get("https://example.com").status_code)
```

Then make the file executable:

```bash
chmod +x script.py
./script.py
```

Use this pattern for checked-in utility scripts that should be runnable from the
shell without asking the caller to remember `uv run`.

## Project isolation rules

There are two distinct cases:

1. Plain script with no inline metadata inside a project:
   - `uv run script.py` includes the project by default
   - `uv run --no-project script.py` skips project discovery, but `uv` can
     still use an active virtual environment or one found in the current or
     parent directories
   - place `--no-project` before the script path
   - use inline metadata, or `uv run --isolated --no-project ...`, when the
     script truly needs a clean ephemeral environment
2. Script with inline metadata:
   - `uv run script.py` runs in the script's isolated environment
   - project dependencies are ignored automatically
   - `--no-project` is not required

This distinction is easy to miss and causes a lot of accidental coupling.

## Locking and reproducibility

Projects get a shared `uv.lock`; scripts do not. For scripts, locking is
explicit:

```bash
uv lock --script script.py
```

That creates an adjacent lockfile such as `script.py.lock`.

Good defaults:

- lock scripts you intend to rerun over time or share with others
- do not assume script locking is automatic
- treat the adjacent `.lock` file as generated state, like project `uv.lock`

For stronger long-term reproducibility, add an `exclude-newer` cutoff in the
inline `tool.uv` section:

```python
# /// script
# dependencies = ["requests"]
# [tool.uv]
# exclude-newer = "2024-01-01T00:00:00Z"
# ///
```

Use this when you need time-bounded resolution rather than "latest compatible
package at run time."

## Alternate indexes

Keep this as an advanced path. When a script truly needs a non-default index,
add it through `uv` so the metadata stays coherent:

```bash
uv add --script script.py --index "https://example.com/simple" private-package
```

Prefer the default index unless the task genuinely requires a private or
mirrored registry.

## Source map

- Script guide: https://docs.astral.sh/uv/guides/scripts/
- Running commands: https://docs.astral.sh/uv/concepts/projects/run/
- CLI reference: https://docs.astral.sh/uv/reference/cli/
- Inline script metadata: https://packaging.python.org/en/latest/specifications/inline-script-metadata/
