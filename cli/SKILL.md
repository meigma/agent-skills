---
name: cli
description: |
  Design, review, and refactor command-line interfaces across languages. Use when creating CLI tools or subcommands, shaping flags/arguments and subcommands, defining stdin/stdout/stderr behavior, exit codes, config and environment precedence, machine-readable output, help/version/completion/manual UX, or auditing a CLI for scriptability, composability, and Unix-style ergonomics. Favors durable CLI conventions over framework-specific patterns.
---

# CLI Design

Design CLIs as small, composable, scriptable tools first. Optimize for pipes, files, automation, and clear contracts. Favor conventions that survive across languages and frameworks: POSIX-style argument handling, GNU-style help and version behavior, and Git-style caution around ambiguous parsing.

## Default Workflow

Before proposing or changing a CLI, decide these explicitly:

1. Command family shape: one command, a few clear subcommands, or a richer command tree.
2. I/O contract: what comes from stdin, what is written to stdout, what is written to stderr, and what files are read or written.
3. Machine interface: whether the command needs a stable structured mode such as `--json`.
4. Config precedence: how flags, environment variables, config files, and defaults interact.
5. Interactive behavior: what happens with and without a TTY, and how destructive actions are confirmed or bypassed in automation.
6. Docs surface: `--help`, `--version`, examples, completion, and manpage expectations.
7. Compatibility plan: what scripts may depend on already and which behaviors must remain stable.

## Rules Of Thumb

- Put data on stdout. Put diagnostics, warnings, prompts, and progress on stderr.
- Default to human-readable output, but provide a stable machine-readable mode when the command is likely to be scripted or integrated.
- Use operands for the main targets or inputs. Use options for behavior, formatting, and output destinations.
- Put options before operands, accept `--` as the end of options, and accept `-` for stdin or stdout when that meaning is natural.
- Prefer explicit output options such as `-o` or `--output` instead of positional output files.
- Use subcommands only when verbs are genuinely distinct. Avoid deep trees with overlapping meanings.
- Make the non-interactive path first-class. A script must be able to use the command without a TTY.
- If confirmation is needed for destructive actions, gate it on TTY presence and provide explicit overrides such as `--yes`, `--force`, `--dry-run`, or `--interactive`.
- Document config precedence as `flags > env > config file > defaults` unless the product has a deliberate, documented reason to differ.
- Keep exit codes meaningful. Use success for success, non-zero for failure, and reserve distinct codes for cases scripts may need to branch on.
- Keep error messages short, specific, and actionable. Say what failed, for which input, and what the user can do next.
- Provide `--help` and `--version` with predictable behavior: print to stdout, ignore unrelated arguments once selected, and exit successfully.
- For mature tools, support examples, shell completion, and manpages or equivalent structured docs.
- Preserve script compatibility. Do not rely on ambiguous positional parsing, unique-prefix long options, or output that changes shape based on cosmetic context.
- Be careful with TTY-sensitive formatting. Color, progress bars, and spinners should be optional or auto-disabled when stdout is not a terminal.
- Treat filenames and user input as hostile to assumptions. Handle spaces, leading dashes, newlines, and paths that require `--` disambiguation.

## Common Failures

- Mixing machine data and human chatter on stdout.
- Requiring prompts, progress UIs, or TTY-only behavior in commands that users will script.
- Hiding destructive behavior behind friendly defaults or vague names.
- Using positional output files or overloaded operands with unclear meaning.
- Letting machine-readable output vary based on TTY detection, color settings, or verbosity flags.
- Growing a subcommand tree where adjacent commands differ only by naming, not by task.
- Returning generic errors that force users to guess which argument, file, or state caused the failure.

## TUI Exception

Treat full-screen terminal UIs as a layer on top of a scriptable core, not as a replacement for one. If a TUI exists, there should usually be an underlying command surface that supports automation, file-based workflows, structured output, and non-interactive use.

## Review Checklist

Use this checklist when designing or reviewing a CLI:

- Can the command be safely composed in a pipeline?
- Can a script run it without a TTY and without hanging on prompts?
- Are stdin, stdout, stderr, files, and exit codes clearly defined?
- Are weird filenames, leading dashes, and `--` handled correctly?
- Is structured output stable enough for automation?
- Are destructive actions previewable, confirmable, or reversible?
- Are `--help`, `--version`, and examples obvious and trustworthy?
- Is configuration precedence documented and unsurprising?
- Does the command do one job clearly, or are responsibilities blurred?
- Would this interface still make sense six months later in a shell script or CI job?

## Scope Notes

- Primary target: Unix-style utilities and multi-command developer tools.
- Secondary target: app-like CLIs, as long as they preserve a scriptable core.
- Out of scope for this skill: framework-specific APIs, language-specific parser libraries, and terminal UI implementation details.
