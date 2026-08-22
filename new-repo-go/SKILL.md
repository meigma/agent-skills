---
name: new-repo-go
description: Create a new Go repository from Meigma's template-go GitHub template. Use when bootstrapping a new Meigma Go project, creating a GitHub repository from meigma/template-go, cloning it into the local ~/code tree, or explaining the first setup steps after template creation.
---

# New Meigma Go Repository

Use this skill when the user wants a new Go repository based on `meigma/template-go`.
The template provides the Meigma baseline: Go module skeleton, Cobra/Viper CLI entrypoint, Moon tasks, pinned CI, Dependabot, repository settings manifest, strict Go linting, docs scaffolding, dormant Release Please/GoReleaser workflows, and `ghd` compatibility metadata.

## Location Rules

- All local repositories live under `~/code`.
- Meigma repositories live under `~/code/meigma`.
- Never clone a Meigma repository into the current working directory unless the user explicitly asks for that.

## Before Creating

Confirm or infer the few inputs that materially affect the command:

- repository name, such as `example-service`
- visibility: `--private`, `--public`, or `--internal`
- short description, if the user provides one
- binary name, if different from the repository name

Check GitHub CLI authentication before attempting creation:

```sh
gh auth status
```

## Create From The Template

For a Meigma repository, create it from `meigma/template-go` while standing in `~/code/meigma` so `--clone` lands in the right place:

```sh
mkdir -p ~/code/meigma
cd ~/code/meigma

gh repo create meigma/REPO_NAME \
  --private \
  --template meigma/template-go \
  --clone
```

Use `--public` or `--internal` instead of `--private` when that is the requested visibility.
Add `--description "..."` when the user provides a useful repository description.

Do not add `--add-readme`, `--gitignore`, or `--license`; the template already supplies repository content and the generated project should decide its final license.
Do not add `--include-all-branches` unless the user explicitly wants every template branch.

For non-Meigma repositories, still create them under `~/code`, but use the requested owner:

```sh
mkdir -p ~/code
cd ~/code

gh repo create OWNER/REPO_NAME \
  --private \
  --template meigma/template-go \
  --clone
```

## First Local Setup

After cloning, enter the repository and start with the template's own onboarding file:

```sh
cd ~/code/meigma/REPO_NAME
sed -n '1,220p' DELETE_ME.md
```

Then perform the basic rename pass:

```sh
go mod edit -module github.com/meigma/REPO_NAME
mv cmd/template-go cmd/BINARY_NAME
rg "template-go|TEMPLATE_GO|github.com/meigma/template-go"
go mod tidy
moon run root:check
```

Update every placeholder found by `rg`, especially:

- Go imports and package docs
- Moon metadata and build output paths
- Cobra command name and Viper environment prefix
- `.goreleaser.yaml`
- `ghd.toml`
- `release-please-config.json`
- README, CONTRIBUTING, SECURITY, and docs text

Delete `DELETE_ME.md` once the first setup checklist is complete.

## Repository Settings

GitHub template repositories copy files and branches, not repository settings.
Branch rules, tag rules, merge settings, vulnerability reporting, repository variables, repository secrets, and environments must be applied separately.

Use the checked-in `.github/repository-settings.toml` as the bootstrap source of truth, or rely on organization-level rulesets when they cover the new repository.
