# SECURITY Guidance

Use this file before writing or reviewing `SECURITY.md`.

## Purpose

`SECURITY.md` exists to give researchers and users a safe path for vulnerability disclosure.

At minimum it should:

1. tell people how to report vulnerabilities privately
2. tell people which versions are supported
3. tell people not to file security issues publicly

## Required Accuracy Rules

Do not invent:

- an email alias
- a HackerOne or bug bounty program
- a GitHub advisory URL
- a support window or version matrix
- acknowledgement or fix timelines

If the reporting channel is not discoverable from repo context, ask the user rather than fabricating one.

## Reporting Channel Order

Prefer this order when choosing a private reporting path:

1. GitHub private vulnerability reporting or repository security advisories, if the repo is on GitHub and the path is real
2. a documented security email alias or team address
3. a dedicated vulnerability submission program such as HackerOne
4. ask the user for the missing channel

Always state that public issues, discussions, and normal support channels are not appropriate for vulnerability reports.

## Supported Versions

Use one of these shapes:

### Version table

Use when the repo already has clear release lines.

```markdown
## Supported Versions

| Version | Supported |
| ------- | --------- |
| 2.x     | Yes       |
| 1.x     | No        |
```

### Short policy statement

Use when the repo has a simpler support model and the claim is grounded in releases or docs.

Example patterns:

- only the latest release is supported
- the latest minor release in the current major line is supported
- the current major and the previous major receive security fixes

Do not claim a support policy that the maintainers have not actually adopted.

## Recommended Sections

```markdown
# Security Policy

## Supported Versions

Supported version table or support policy.

## Reporting a Vulnerability

Private reporting channel.
Clear instruction not to use public issues.
Requested report details if appropriate.

## Disclosure Process

Only include if the process is real and stable.
```

## Optional but Good

- expected acknowledgement window
- what details reporters should include
- advisory publication location
- coordinated disclosure notes

## Good Defaults

- concise is better than elaborate
- private reporting path should be near the top
- advisory publication location can point to the repo's GitHub advisories page when real
- if GitHub private reporting is enabled, the security file should still tell people not to use public issues

## SECURITY Review Checklist

- Is there a real private reporting path?
- Does it say not to report publicly?
- Are supported versions described in a defensible way?
- Is any SLA or response promise actually backed by project policy?
- Does it avoid mixing security reporting with bug support?
