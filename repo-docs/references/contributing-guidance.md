# CONTRIBUTING Guidance

Use this file when drafting or reviewing `CONTRIBUTING.md`.

## Purpose

`CONTRIBUTING.md` should help contributors do the right thing on the first try and help maintainers avoid preventable churn.

It should answer:

1. where should questions, bugs, and features go?
2. what does a good contribution look like?
3. how do I prepare and submit a change?

## Two Valid Shapes

### Short pointer doc

Use when the canonical contributor guide already lives elsewhere.

```markdown
# Contributing

Thanks for your interest in contributing.

For contributor setup, workflow, and review expectations, see the full guide:
[Contributor Guide](https://example.com/contributing)

Please use normal issue channels for bugs and features, and use
[SECURITY.md](SECURITY.md) for vulnerability reporting.
```

### Root-level operating guide

Use when the repository itself should contain the main contributor instructions.

```markdown
# Contributing

## Asking Questions

Where support questions belong.

## Reporting Bugs

How to file a reproducible bug report.

## Proposing Features

Whether maintainers prefer prior discussion.

## Pull Requests

Branch, test, docs, and review expectations.

## Code of Conduct

Link to the policy.
```

## Recommended Sections

- welcome and scope
- asking questions or getting support
- reporting bugs
- proposing features
- pull request workflow
- local setup, testing, or docs expectations
- Code of Conduct

## Include Only If Real

- CLA requirements
- DCO sign-off requirements
- AI or LLM disclosure policy
- maintainer approval workflow specifics
- release backport policy

## Routing Rules

Make these distinctions explicit:

- support questions are not bug reports
- security vulnerabilities should go to `SECURITY.md`
- large changes may need prior discussion before implementation

If the project uses issue templates, discussions, or external forums, route contributors there clearly.

## PR Expectations

Strong default expectations:

- keep changes focused
- include tests when behavior changes
- update docs when user-facing behavior changes
- explain the change clearly in the PR
- ensure CI passes before requesting review

Only mention branch naming, commit conventions, changelog fragments, or labels if the repo actually uses them.

## Bug Report Guidance

Ask for concrete inputs:

- environment or version
- reproducible steps
- expected behavior
- actual behavior
- logs, screenshots, or minimal repro when appropriate

## Tone

Contributing docs can be welcoming without becoming chatty.

Prefer:

- clear routing
- direct instructions
- specific expectations

Avoid:

- guilt-driven wording
- vague requests to "be respectful" without linking the Code of Conduct
- legal or process language that the repo does not actually enforce

## CONTRIBUTING Review Checklist

- Can a contributor tell where to ask a question versus file a bug?
- Does it route security reports to `SECURITY.md`?
- Are PR expectations concrete and repo-specific?
- Does it avoid fake process, fake legal requirements, and filler text?
- If a fuller guide exists elsewhere, is the root file short and direct instead of duplicative?
