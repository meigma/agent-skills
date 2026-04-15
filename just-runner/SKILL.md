---
name: just-runner
description: Command runner using just (justfile). Use when creating or editing justfiles, writing recipes, running project commands, automating tasks, or when the user mentions just, justfile, or asks about command runners as an alternative to make/Makefile. Covers recipe syntax, arguments, variables, dependencies, shebang recipes, modules, settings, and CLI usage.
---

# Just Command Runner

`just` is a command runner for project-specific tasks. Unlike `make`, it's designed for running commands, not building software.

## Quick Start

Create a `justfile` in your project root:

```just
# Build the project
build:
    cargo build --release

# Run tests
test: build
    cargo test

# Default recipe (runs when you type `just`)
default: test
```

Run with `just`, `just build`, or `just test`.

## Syntax Essentials

- **Indentation**: Use 4 spaces or tabs consistently (not both)
- **Comments**: Lines starting with `#`
- **Recipe names**: lowercase with hyphens (`my-recipe`)
- **Variables**: `name := "value"` (immutable)
- **String interpolation**: `{{variable}}` in recipe bodies

## Recipes

### Basic Recipe

```just
build:
    echo "Building..."
    cargo build
```

### Default Recipe

The first recipe runs by default, or name one `default`:

```just
default: build test

build:
    cargo build

test:
    cargo test
```

### Private Recipes

Hidden from `just --list`:

```just
# Prefix with underscore
_helper:
    echo "I'm hidden"

# Or use attribute
[private]
also-hidden:
    echo "Also hidden"
```

### Quiet Recipes

Suppress command echoing:

```just
# @ prefix suppresses echo for entire recipe
@quiet-recipe:
    echo "Only output shows"

# @ on individual lines
mixed:
    echo "This command is printed"
    @echo "This command is hidden"
```

Or globally:

```just
set quiet

all-quiet:
    echo "Commands not echoed"
```

## Shebang Recipes

Execute with any interpreter:

```just
python-script:
    #!/usr/bin/env python3
    import json
    print(json.dumps({"status": "ok"}))

bash-script:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Strict bash mode"

node-script:
    #!/usr/bin/env node
    console.log("Hello from Node!")
```

## Arguments

### Positional Arguments

```just
greet name:
    echo "Hello, {{name}}!"

# just greet World
```

### Default Values

```just
serve port="8080":
    ./server --port {{port}}

# just serve        -> uses 8080
# just serve 3000   -> uses 3000
```

### Variadic Arguments

```just
# One or more arguments (required)
test +files:
    cargo test {{files}}

# Zero or more arguments (optional)
run *args:
    ./program {{args}}
```

### Environment Variable Arguments

Prefix with `$` to export as environment variable:

```just
build $PROFILE="dev":
    cargo build --profile $PROFILE
```

### Positional Arguments Setting

Access arguments as `$1`, `$2`, etc.:

```just
set positional-arguments

@test *args:
    bash -c 'for arg; do echo "- $arg"; done' -- "$@"
```

## Variables

### Assignment

```just
version := "1.0.0"
build_dir := "target/release"

build:
    echo "Building {{version}} to {{build_dir}}"
```

### Backtick Evaluation

Capture command output:

```just
git_hash := `git rev-parse --short HEAD`
date := `date +%Y-%m-%d`

info:
    echo "Commit: {{git_hash}}, Date: {{date}}"
```

### Environment Variables

```just
# Read environment variable
home := env('HOME')
port := env('PORT', '8080')  # with default

# Export to recipes
export DATABASE_URL := "postgres://localhost/mydb"

migrate:
    # $DATABASE_URL available here
    ./migrate up
```

### Conditional Expressions

```just
os := if os() == "macos" { "darwin" } else { os() }

profile := if env('CI', '') != '' { "release" } else { "dev" }

build:
    cargo build --profile {{profile}}
```

## Dependencies

### Prior Dependencies

Run before recipe:

```just
test: build
    cargo test

build:
    cargo build
```

### Subsequent Dependencies

Run after recipe with `&&`:

```just
all: build && test deploy
    echo "Build complete"

# Order: build -> "Build complete" -> test -> deploy
```

### Dependencies with Arguments

```just
push: (build "release")
    git push

build profile:
    cargo build --profile {{profile}}
```

## Recipe Attributes

### Documentation

```just
# Comment above becomes doc
build:
    cargo build

# Override with attribute
[doc('Custom documentation')]
deploy:
    ./deploy.sh
```

### Confirmation Prompt

```just
[confirm]
delete-all:
    rm -rf data/

[confirm("Delete production database?")]
drop-db:
    psql -c "DROP DATABASE prod"
```

### Groups

Organize recipes in `--list` output:

```just
[group('build')]
build:
    cargo build

[group('build')]
release:
    cargo build --release

[group('test')]
test:
    cargo test
```

### OS-Specific Recipes

```just
[linux]
install:
    apt install package

[macos]
install:
    brew install package

[windows]
install:
    choco install package

[unix]  # linux + macos
unix-only:
    ./unix-script.sh
```

### Working Directory

```just
[working-directory: 'frontend']
build-frontend:
    npm run build

[no-cd]  # Run in invocation directory, not justfile directory
pwd:
    pwd
```

### Suppress Error Messages

```just
[no-exit-message]
git *args:
    @git {{args}}
```

## Dotenv Integration

```just
set dotenv-load

# Or specify file
set dotenv-filename := ".env.local"
set dotenv-path := "/etc/myapp/.env"

serve:
    echo "Starting on port $PORT"
```

## Settings

```just
# Shell configuration
set shell := ["bash", "-euo", "pipefail", "-c"]
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# Behavior
set dotenv-load                    # Load .env file
set export                         # Export all variables
set positional-arguments           # Enable $1, $2, etc.
set quiet                          # Suppress command echo
set fallback                       # Search parent directories
set allow-duplicate-recipes        # Last definition wins
set ignore-comments                # Don't pass comments to shell
set tempdir := "/tmp"              # Temp file location
set working-directory := "src"     # Default working directory
```

## Modules

Organize large projects:

```just
# justfile
mod frontend 'frontend/justfile'
mod backend

default:
    @just --list

# Run submodule recipe
build: frontend::build backend::build
```

```just
# frontend/justfile
build:
    npm run build

dev:
    npm run dev
```

Invoke with `just frontend build` or `just frontend::build`.

### Optional Modules

```just
mod? local  # No error if missing
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `just` | Run default recipe |
| `just recipe` | Run specific recipe |
| `just recipe arg1 arg2` | Run with arguments |
| `just --list` | List available recipes |
| `just --summary` | One-line recipe list |
| `just --show recipe` | Show recipe source |
| `just --evaluate` | Print variable values |
| `just --dry-run recipe` | Show what would run |
| `just --choose` | Interactive recipe selection |
| `just --fmt --unstable` | Format justfile |
| `just --dump` | Output formatted justfile |
| `just --groups` | List recipe groups |
| `just --completions SHELL` | Generate shell completions |

## Built-in Functions

See [references/functions.md](references/functions.md) for complete reference.

Common functions:

```just
# System
os := os()                      # "linux", "macos", "windows"
arch := arch()                  # "x86_64", "aarch64"
cpus := num_cpus()              # Number of CPUs

# Paths
abs := absolute_path("rel")     # Convert to absolute
name := file_name("/a/b.txt")   # "b.txt"
stem := file_stem("/a/b.txt")   # "b"
ext := extension("/a/b.txt")    # "txt"
parent := parent_directory("/a/b")  # "/a"
exists := path_exists("file")   # "true" or "false"

# Strings
upper := uppercase("hello")     # "HELLO"
lower := lowercase("HELLO")     # "hello"
replaced := replace("ab", "a", "x")  # "xb"
trimmed := trim("  hi  ")       # "hi"

# Environment
home := env('HOME')
port := env('PORT', '3000')

# Errors
check := if path_exists("x") == "true" { "ok" } else { error("missing x") }
```

## Best Practices

1. **Name the default recipe `default`** for clarity
2. **Document public recipes** with comments above them
3. **Use `[private]` for helpers** that shouldn't be listed
4. **Group related recipes** with `[group]` attributes
5. **Use shebang recipes** for complex scripts instead of escaped shell
6. **Set strict shell mode** for bash: `set shell := ["bash", "-euo", "pipefail", "-c"]`
7. **Load `.env` files** with `set dotenv-load` for configuration
8. **Use modules** for large projects to organize by domain
9. **Provide defaults** for optional arguments
10. **Use `@` prefix** for clean output on simple recipes

## Common Patterns

### CI/CD Commands

```just
set dotenv-load
set shell := ["bash", "-euo", "pipefail", "-c"]

default:
    @just --list

# Development
dev: install
    ./scripts/dev.sh

install:
    npm ci

# Testing
test: lint unit-test integration-test

[group('test')]
lint:
    npm run lint

[group('test')]
unit-test:
    npm test

[group('test')]
integration-test:
    npm run test:integration

# Deployment
[confirm("Deploy to production?")]
[group('deploy')]
deploy: test
    ./scripts/deploy.sh
```

### Polyglot Project

```just
build: build-go build-rust build-node

build-go:
    cd go && go build ./...

build-rust:
    cd rust && cargo build

build-node:
    cd node && npm run build
```

### Docker Commands

```just
image := "myapp"
tag := `git describe --tags --always`

build:
    docker build -t {{image}}:{{tag}} .

run *args:
    docker run --rm -it {{image}}:{{tag}} {{args}}

push: build
    docker push {{image}}:{{tag}}
```
