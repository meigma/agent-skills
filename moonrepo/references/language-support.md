# Language Support Notes

Assistant-facing summary of the current Moon v2 language and toolchain surface.

## Primary docs

- Support matrix and tiers: https://moonrepo.dev/docs
- Language model and `system` toolchain: https://moonrepo.dev/docs/how-it-works/languages
- Toolchains config: https://moonrepo.dev/docs/config/toolchain
- Migration guide: https://moonrepo.dev/docs/migrate/2.0

## Grounded rules

1. Use the support matrix in the live docs for current tier expectations. Do not rely on old
   `unstable_*` naming outside Python.
2. `go` and `rust` are stable toolchains in v2. The local CLI confirms this via
   `moon toolchain info go` and `moon toolchain info rust`.
3. Python remains unstable in v2. Keep `unstable_python`, and use `unstable_pip` or
   `unstable_uv` when needed.
4. `bun`, `deno`, and `node` require `javascript` to also be enabled.
5. When a task is just a shell command or a binary already on `PATH`, set the task
   `toolchain` to `system`.
6. When you need exact per-toolchain settings, prefer `moon toolchain info <id>` over copied
   tables in this skill.

## Vetted examples

### JavaScript plus Node

```yaml
javascript:
  packageManager: 'pnpm'

node:
  version: '24.0.0'
```

### Stable Go and Rust

```yaml
go:
  version: '1.24.0'

rust:
  version: '1.87.0'
  components: ['clippy', 'rustfmt']
```

### Python remains unstable

```yaml
unstable_python:
  version: '3.12.0'
  packageManager: 'uv'

unstable_uv:
  version: '0.8.0'
```

### System task for non-integrated commands

```yaml
tasks:
  dockerBuild:
    command: 'docker build -t app .'
    toolchain: 'system'
```

## Guidance to keep

- Treat toolchain IDs as live CLI facts, not lore.
- Prefer supported ecosystem inference where Moon already parses manifests and lockfiles.
- Use `dependsOn` for cross-ecosystem or non-manifest relationships instead of forcing
  unsupported inference.

## Guidance to avoid

- Do not teach older unstable Go or Rust identifiers.
- Do not frame Rust as a special WASM-only toolchain path in v2.
- Do not claim Python is fully stable.
