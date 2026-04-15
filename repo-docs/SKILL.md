---
name: repo-docs
description: Create and update standard repository docs for software repos, especially README.md, SECURITY.md, and CONTRIBUTING.md. Use when bootstrapping repo-adjacent docs, refreshing community health files, reviewing whether those docs follow established open-source conventions, or drafting them from repository context. Produces restrained, practical docs without emojis, hype, or invented governance or security details.
---

# Repo Docs

Write and update the standard root-level repository docs that orient users, contributors, and security reporters.

This skill is for the common doc set together:

- `README.md`
- `SECURITY.md`
- `CONTRIBUTING.md`

If the request is only about README quality, this skill can still handle it, but it should keep the other two files in mind so the repo-level docs stay consistent.

## Workflow

1. Read repository context before drafting:
   - existing root docs and `docs/`
   - `LICENSE*`, `CODE_OF_CONDUCT*`, `SUPPORT*`, issue and PR templates, `.github/`
   - install/build/test entry points such as `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `Makefile`, `justfile`
   - CI workflows, release notes, tags, and changelog files
   - git remote when reporting URLs or documentation links depend on hosting
2. Decide whether to:
   - create new files
   - update existing files
   - keep a short root-level pointer doc that links to a canonical external guide
3. Keep the trio internally consistent:
   - `README.md` links to `CONTRIBUTING.md` and `SECURITY.md`
   - `CONTRIBUTING.md` routes security issues to `SECURITY.md`
   - `SECURITY.md` does not duplicate normal support or bug-report channels
4. Prefer concise root docs. Link outward for detailed process or architecture docs rather than copying them into the root files.
5. Match the repo's actual operating model. If a fact cannot be grounded in repository context, either omit the claim or ask.

## Non-Negotiables

- Keep the tone factual, restrained, and low-noise.
- Do not use emojis unless the user explicitly asks for them.
- Do not default to decorative badge walls.
- Do not use hype, slogans, or empty claims.
- Use relative links for repo-local files.
- Keep root docs scannable and front-load the most useful information.
- Never invent:
  - security contacts, aliases, or reporting URLs
  - support SLAs or response times
  - CLA or DCO requirements
  - governance structures or maintainer roles
  - supported version windows
  - build, install, or release commands not supported by the repo

## File Strategy

### README.md

The README is an orientation document, not a full manual.

Load [references/readme-guidance.md](references/readme-guidance.md) when drafting or reviewing a README.

### SECURITY.md

`SECURITY.md` is safety-critical. Accuracy matters more than speed or completeness.

Load [references/security-guidance.md](references/security-guidance.md) before writing or revising a security policy.

### CONTRIBUTING.md

`CONTRIBUTING.md` should reduce maintainer churn by routing contributors correctly and stating expectations early.

Load [references/contributing-guidance.md](references/contributing-guidance.md) before drafting contributor guidance.

## Root Doc Defaults

Use these defaults unless repo context suggests a different shape.

### Default README shape

1. Title
2. One to three sentence description
3. Quick start, install, or build
4. Minimal usage example when helpful
5. Documentation or support links
6. Contributing
7. Security
8. License

### Default SECURITY shape

1. Security policy title
2. Supported versions or support policy
3. Reporting a vulnerability
4. Optional acknowledgement timeline, only if real
5. Optional advisory publication location

### Default CONTRIBUTING shape

1. Welcome and scope
2. Where to ask questions
3. Reporting bugs
4. Proposing features
5. Pull request process
6. Local setup, testing, or docs expectations
7. Code of Conduct link
8. CLA or DCO section only if the repo actually requires it

## Decision Rules

- If the repo already has a canonical contributor or security guide elsewhere, the root file may be a short pointer doc.
- If the repo is mature and its operational details live on a website or wiki, keep root files shorter and link to canonical sources.
- If the repo is small or early-stage, prefer self-contained docs that let someone use and contribute without leaving the repository.
- If the repo already has an established voice, preserve it while removing avoidable fluff and ambiguity.
- If the user asks for a review instead of a draft, focus on missing routing, invented claims, stale commands, and mismatch between docs and actual repo behavior.

## Final Check

Before finishing, verify:

- all internal links resolve
- commands match the actual toolchain
- `README.md`, `SECURITY.md`, and `CONTRIBUTING.md` point to each other appropriately
- support, bugs, and vulnerabilities are clearly routed to different channels
- no section claims a process, policy, or contact that the repo does not actually have
