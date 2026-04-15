---
name: charmbracelet
description: Use when building beautiful Go CLI apps with Charmbracelet packages other than Bubble Tea. Covers Lip Gloss for styling and layout, Huh for forms and prompts, and Log for colorful structured CLI logging, including shared theming and integration points between them.
---

# Charmbracelet CLI Packages

Use this skill when the task is about `charm.land/lipgloss/v2`, `charm.land/huh/v2`, or `charm.land/log/v2` in Go CLIs. It focuses on terminal styling, forms and prompts, and structured logging. Keep Bubble Tea architecture out of scope here beyond brief integration notes such as "Huh forms are `tea.Model`s" or "Lip Gloss pairs well with Bubble Tea views."

Validated package surface on April 10, 2026:
- `charm.land/lipgloss/v2` `v2.0.2`
- `charm.land/huh/v2` `v2.0.3`
- `charm.land/log/v2` `v2.0.0`

## Use This Package When

- `lipgloss`: you need styling, layout, spacing, borders, tables, lists, trees, measurement, or terminal-safe color handling.
- `huh`: you need blocking forms or prompts with grouped pages, validation, themes, accessible mode, or dynamic fields.
- `log`: you need human-readable structured logs, Lip Gloss-powered log styling, `slog` integration, or a `*log.Logger` adapter for packages that only accept the standard logger.

## Integration Map

- `huh` themes are built from Lip Gloss styles. Use a shared palette to keep prompts and summaries consistent.
- `log` styles are Lip Gloss styles. Match log level colors to the same palette you use for prompts and summaries.
- Use Lip Gloss to render summaries, status blocks, tables, and framing around Huh-driven input flows and Log-driven output.
- If the task becomes about Bubble Tea state machines, commands, or MVU composition, switch to the Bubble Tea skill.

## Read These Files As Needed

- [references/lipgloss.md](references/lipgloss.md): choosing Lip Gloss, layout and styling patterns, tables and lists, measurement, and footguns.
- [references/huh.md](references/huh.md): choosing Huh, field types, accessible mode, theming, dynamic forms, and spinner usage.
- [references/log.md](references/log.md): choosing Log, levels, structured logging, styles, `slog`, standard-log adapter, and v1-to-v2 import migration.
- [references/patterns.md](references/patterns.md): cross-package patterns that combine all three packages with source lineage.

## Working Rules

- Use only claims that can be traced to official upstream READMEs, example files, `pkg.go.dev` docs, or verified module metadata.
- Default to `charm.land/.../v2` imports. Mention the old GitHub import path only when migrating Log v1 code.
- Prefer compile-checked examples over loose snippets.
- Do not teach Bubble Tea architecture here; keep that for the dedicated Bubble Tea skill.
