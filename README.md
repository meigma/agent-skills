# agent-skills

An opinionated collection of [Claude Code](https://docs.claude.com/en/docs/claude-code) agent skills for
software engineering workflows — building Go CLIs and libraries, writing tests,
shipping releases, running CI, and producing documentation.

Each subdirectory is a self-contained skill with a `SKILL.md` and optional
reference material. Skills are designed to be dropped into a Claude Code
installation at `~/.claude/skills/` (user scope) or `.claude/skills/` (project
scope).

## Skills

| Skill | Summary |
| --- | --- |
| [charmbracelet](charmbracelet/) | Build Go CLIs with Lip Gloss, Huh, and Log (excluding Bubble Tea). |
| [cli](cli/) | Design and audit command-line interfaces for scriptability and Unix ergonomics. |
| [cobra-viper-cli](cobra-viper-cli/) | Build production-ready Go CLIs with Cobra and Viper. |
| [diataxis](diataxis/) | Organize documentation into tutorials, how-to guides, reference, and explanation. |
| [docusaurus](docusaurus/) | Configure and extend Docusaurus documentation sites. |
| [gh-cli](gh-cli/) | Work with GitHub via the `gh` CLI for PRs, Actions, issues, repo settings, and API calls. |
| [github-actions](github-actions/) | Write and harden GitHub Actions workflows for CI/CD. |
| [go-benchmarking](go-benchmarking/) | Write and analyze Go benchmarks with `b.Loop` and benchstat. |
| [go-testscript](go-testscript/) | Test Go CLIs with `rsc.io/script`-style testscript and txtar files. |
| [goreleaser](goreleaser/) | Release Go binaries with GoReleaser, Cosign, SBOMs, and Homebrew. |
| [just-runner](just-runner/) | Write `justfile` recipes as a modern alternative to Make. |
| [moonrepo](moonrepo/) | Configure monorepos with moon v2 — workspace, toolchains, and tasks. |
| [readme-writer](readme-writer/) | Draft clear, professional READMEs without marketing fluff. |
| [release-please](release-please/) | Automate releases with release-please and Conventional Commits. |
| [repo-docs](repo-docs/) | Bootstrap README, SECURITY, and CONTRIBUTING for software repos. |
| [testcontainers-go](testcontainers-go/) | Write Go integration tests backed by real containerized dependencies. |
| [worktrunk](worktrunk/) | Manage isolated Git worktrees with Worktrunk and prefer `gh pr` over local merge flow. |

## Installation

Clone the repo and symlink (or copy) skills into your Claude Code skills
directory:

```sh
git clone https://github.com/meigma/agent-skills.git
cd agent-skills

# Install a single skill to user scope
ln -s "$PWD/cobra-viper-cli" ~/.claude/skills/cobra-viper-cli

# Or install all skills
for d in */; do
    ln -s "$PWD/${d%/}" ~/.claude/skills/"${d%/}"
done
```

For project scope, symlink into `.claude/skills/` inside the target repository
instead.

## Using a Skill

Skills activate automatically when their `description` matches the current
task. You can also invoke one explicitly in Claude Code:

```
/skill cobra-viper-cli
```

See the [Claude Code skills documentation](https://docs.claude.com/en/docs/claude-code/skills)
for details on skill discovery and scoping.

## Contributing

Issues and pull requests are welcome. New skills should follow the layout of
the existing ones: a top-level `SKILL.md` with YAML frontmatter (`name`,
`description`) and any longer reference material under a `references/` (or
topic-named) subdirectory.

## License

Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or
  <http://www.apache.org/licenses/LICENSE-2.0>)
- MIT License ([LICENSE-MIT](LICENSE-MIT) or
  <http://opensource.org/licenses/MIT>)

at your option.

### Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in this work by you, as defined in the Apache-2.0 license, shall
be dual licensed as above, without any additional terms or conditions.
