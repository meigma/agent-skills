---
name: readme-writer
description: Write professional README documentation for software projects. Use when creating new READMEs, improving existing documentation, or reviewing README quality. Activates for requests involving README.md files, project documentation, repository setup, or when users ask for help documenting their code. Produces clean, professional READMEs without excessive emojis or marketing language.
---

# README Writer

Write clear, professional README documentation that helps users understand, use, and contribute to software projects.

## Core Principles

1. **Clarity over creativity** - README is documentation, not marketing material
2. **Progressive disclosure** - Essential info first, details later
3. **Actionable content** - Every section should help the reader do something
4. **Professional tone** - Factual, direct, minimal embellishment

## Section Reference

### Required Sections

**Title**
- Match the project/package name exactly
- No taglines or slogans in the title itself

**Description**
- 1-3 sentences explaining what the project does
- State the problem it solves or its primary use case
- Avoid superlatives ("blazingly fast", "revolutionary", "the best")

**Installation**
- Provide copy-paste commands
- Cover the primary installation method first
- Include prerequisites if non-obvious

**Usage**
- Show a minimal working example
- Include the most common use case
- Use realistic, not contrived, examples

**License**
- State the license name (e.g., "MIT License")
- Link to the LICENSE file

### Recommended Sections

**Table of Contents** - Include if README exceeds ~100 lines

**Features** - Brief list of key capabilities (not a sales pitch)

**Configuration** - Document options, environment variables, config files

**API Reference** - For libraries: document exported functions/types

**Contributing** - How to submit issues, PRs, and coding standards

**Acknowledgments** - Credit dependencies, inspiration, contributors

### Optional Sections

**Badges** - Keep minimal (build status, version, license). Avoid decorative badges.

**Screenshots/GIFs** - Only if they genuinely aid understanding

**Roadmap** - Only if actively maintained

**FAQ** - Only if the same questions arise repeatedly

## Tone Guidelines

### Avoid

- Excessive emojis (one or two for visual hierarchy is acceptable, a dozen is not)
- Marketing language ("revolutionary", "game-changing", "delightful")
- Unnecessary enthusiasm ("We're so excited to...", "You'll love...")
- Vague descriptions ("A powerful tool for...")
- Jokes or memes in technical sections

### Prefer

- Direct statements ("This library parses JSON" not "A JSON parsing solution")
- Factual claims ("Processes 10k requests/sec" not "blazingly fast")
- Imperative mood for instructions ("Install the package" not "You should install")
- Technical precision over accessibility theater

## Project Type Guidance

### Libraries/Packages

Prioritize: Installation, API docs, usage examples, type signatures
```markdown
## Installation
npm install libname

## Usage
import { parse } from 'libname'
const result = parse(input)

## API
### parse(input: string): Result
Parses the input string and returns...
```

### CLI Tools

Prioritize: Installation, command reference, common workflows
```markdown
## Installation
brew install toolname

## Usage
toolname [command] [flags]

## Commands
- `init` - Initialize a new project
- `build` - Build the project
- `serve` - Start development server
```

### Applications/Frameworks

Prioritize: Quick start, architecture overview, configuration
```markdown
## Quick Start
git clone ...
cd project
./setup.sh
open http://localhost:3000

## Architecture
Brief explanation of how components interact.

## Configuration
Document environment variables and config files.
```

## Quality Checklist

Before finalizing a README, verify:

- [ ] Can a new user understand what this project does in 30 seconds?
- [ ] Can they install and run a basic example in under 5 minutes?
- [ ] Are all code examples tested and working?
- [ ] Is the license clearly stated?
- [ ] Are there no broken links?
- [ ] Is the tone consistent and professional throughout?

## References

- For full README examples across project types, see [references/examples.md](references/examples.md)
- For common mistakes and how to fix them, see [references/anti-patterns.md](references/anti-patterns.md)
