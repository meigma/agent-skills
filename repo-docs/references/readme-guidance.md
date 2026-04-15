# README Guidance

Use this file when drafting or reviewing `README.md`.

## Purpose

The README should let a new visitor answer, quickly:

1. What is this repository?
2. How do I use or build it?
3. Where do I go next?

If it tries to answer everything, it becomes a poor front door.

## Default Shape

Use this as a starting outline, then remove sections that do not earn their place.

```markdown
# Project Name

One to three sentences describing what the project does and where it fits.

## Quick Start

Primary install or build path.

## Usage

Minimal working example or most common workflow.

## Documentation

Links to docs, examples, or architecture notes.

## Support

Where to ask questions or report non-security bugs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).

## License

Licensed under the [MIT License](LICENSE).
```

## Section Selection

### Usually include

- project title
- concise description
- quick start, install, or build instructions
- usage example or command snippet
- documentation link
- contributing link
- security link
- license

### Include only when useful

- features list
- configuration section
- API summary
- troubleshooting
- roadmap
- screenshots or diagrams
- acknowledgments

### Usually omit by default

- long mission statements
- donation sections
- sponsor walls
- giant maintainer rosters
- detailed governance notes
- full changelog content

## Project-Type Patterns

### Libraries

Prioritize installation, the smallest realistic code example, API entry points, and version compatibility if known.

### CLI tools

Prioritize installation, a one-command example, common subcommands, and configuration or environment notes.

### Applications or services

Prioritize local setup, how to run the app, required dependencies, and links to deeper architecture or deployment docs.

### Infrastructure or platform repos

Prioritize what the repo contains, how to build or develop it, where end-user docs live, and where support questions belong.

## Tone

Prefer:

- direct statements
- specific claims
- imperative instructions
- realistic examples

Avoid:

- superlatives
- marketing adjectives
- apology or enthusiasm padding
- emoji-heavy headings
- decorative punctuation

## Badges and Images

- Badges are optional, not required.
- If used, keep them minimal and functional: build status, version, license.
- Prefer no badges over noisy badges.
- Include an image only when it materially improves understanding, such as a product screenshot or architecture diagram.

## README Review Checklist

- Can a new reader understand the repo in under 30 seconds?
- Does at least one install, build, or usage path work from the docs as written?
- Are the links to `CONTRIBUTING.md` and `SECURITY.md` present?
- Is the README duplicating a larger manual that should stay elsewhere?
- Does the tone read like documentation rather than promotion?
