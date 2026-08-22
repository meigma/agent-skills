---
name: tmux-interactive
description: |
  Run and test interactive terminal programs (TUIs, REPLs, debuggers, installers, coding-agent CLIs) by driving them in detached tmux sessions. Use when a program needs typed input mid-run, when testing an interactive CLI end-to-end, when verifying terminal rendering, or when automating expect-style dialogues. Triggers on tmux, send-keys, capture-pane, interactive CLI testing, REPL automation, driving full-screen terminal UIs, or "the command hangs waiting for input".
---

# Driving interactive terminal programs with tmux

tmux is a daemon: a session created in one Bash call is still alive in the next, which makes it the right tool for driving programs that need typed input mid-run. It emulates a full terminal (including the alternate screen used by TUIs), captures clean plain text, and lets the user attach to watch or rescue a session at any time.

## When to use

Use tmux when the program reads input interactively after starting: REPLs, debuggers, installers and wizards, `git rebase -i`, ssh sessions, full-screen TUIs, or coding-agent CLIs under test.

Do NOT use tmux for:

- One-shot commands — run them directly.
- Programs that accept input via stdin redirection, flags, or here-docs (`psql -c`, `python script.py`, `cmd <<EOF`) — prefer those; they are simpler and deterministic.
- Non-interactive long-runners (dev servers, watchers) — use background Bash instead.

## Conventions

Every tmux command in this skill uses a private socket so agent sessions never touch the user's tmux server:

```bash
tmux -L claude-agent ...
```

Rules:

- Always pass `-L claude-agent`. Plain `tmux` talks to the user's server — never kill or send keys there.
- Shell state does not persist between Bash tool calls: spell out the full `tmux -L claude-agent` prefix every time; do not rely on aliases, functions, or exported variables.
- One session per task, with a descriptive name. Check `has-session` before reusing a name.
- Always target explicitly with `-t <session>` (or `-t <session>:<window>.<pane>`).
- If you are running inside the user's tmux (`$TMUX` is set), `new-session` refuses to nest — prefix session-creating commands with `env -u TMUX`.

Helper scripts live in `~/.claude/skills/tmux-interactive/scripts/`. Call them as black boxes — run with `-h` for usage; do not read their source into context.

## Session lifecycle

### 1. Create — detached, explicitly sized, deep history

```bash
env -u TMUX tmux -L claude-agent -f /dev/null \
  set-option -g history-limit 50000 \; \
  new-session -d -s mytask -c /path/to/workdir -x 200 -y 50
```

- `-x 200 -y 50`: detached sessions otherwise default to 80x24, which mangles TUI layouts. Size it like a real terminal.
- `-f /dev/null`: config-free server, no user-config surprises (only matters on the first command, which starts the server).
- `-c`: working directory for the shell.
- This starts a plain shell, not your program. That is deliberate — see shell-first below.

### 2. Wait for the shell prompt before the first send

The #1 flake source: `send-keys` fired immediately after `new-session` lands before the shell finishes initializing and is silently eaten. Always wait first:

```bash
~/.claude/skills/tmux-interactive/scripts/wait-for-text.sh -t mytask '([$%#>]|❯) *$'
```

That regex covers common prompts including starship's `❯`. If it times out, the dump on stderr shows what the pane actually displays — adjust the pattern to match it.

### 3. Launch the program inside the shell (shell-first)

```bash
tmux -L claude-agent send-keys -t mytask -l -- 'python3 -q'
tmux -L claude-agent send-keys -t mytask Enter
~/.claude/skills/tmux-interactive/scripts/wait-for-text.sh -t mytask '>>> *$'
```

If the program crashes, the pane survives and the crash output is still capturable. If you instead pass the program directly to `new-session`, a crash destroys the pane and its output. (Alternative: `set-option -t mytask remain-on-exit on`.)

### 4. Tell the user how to watch

After starting a session, print the attach command so the user can observe live:

```
To watch: tmux -L claude-agent attach -t mytask    (detach with Ctrl+b d)
```

### 5. Clean up when done

```bash
tmux -L claude-agent kill-session -t mytask
tmux -L claude-agent kill-server        # sweep everything on the private socket
```

Never run `kill-server` without `-L claude-agent`.

## Waiting: never send blind

Sleeping a fixed time and hoping is the main source of flaky interaction. Three synchronization tools, in order of preference:

**1. Known pattern → `wait-for-text.sh`** — poll until the pane matches a regex:

```bash
~/.claude/skills/tmux-interactive/scripts/wait-for-text.sh -t mytask -T 30 'Password:'
~/.claude/skills/tmux-interactive/scripts/wait-for-text.sh -t mytask -F 'literal (string)'   # -F = fixed string
```

Exit 0 on match, exit 1 on timeout (dumps the last pane content to stderr so you can see what actually happened).

**2. Unknown prompt / streaming output → `wait-for-idle.sh`** — wait until the screen stops changing:

```bash
~/.claude/skills/tmux-interactive/scripts/wait-for-idle.sh -t mytask -s 2 -T 60
```

`-s` is the stability window: how many seconds the pane must stay unchanged to count as idle. Use `-s 2` for UI settling, `-s 5` or more for programs that stream with pauses (LLM output).

**3. Plain shell commands → deterministic completion with `wait-for`:**

```bash
tmux -L claude-agent send-keys -t mytask -l -- 'make test; tmux -L claude-agent wait -S done'
tmux -L claude-agent send-keys -t mytask Enter
timeout 180 tmux -L claude-agent wait done
```

The suffix signals a tmux channel when the command finishes; `tmux wait done` blocks until then. Only works where a shell parses the suffix — never inside a REPL, editor, or TUI. Note `tmux wait-for` never watches pane *content*; it is only this channel rendezvous.

## Sending input

```bash
tmux -L claude-agent send-keys -t mytask -l -- 'text to type'   # 1. text: literal mode
sleep 0.3                                                        # 2. let the program register it
tmux -L claude-agent send-keys -t mytask Enter                   # 3. Enter: separate call, named key
```

Rules:

- **Always `-l --` for payload text.** Without `-l`, any word matching a key name (`Enter`, `Space`, `C-c`, `Up`) is interpreted as that key. The `--` stops option parsing so text starting with `-` works.
- **Send Enter as a separate call.** `send-keys -t x 'text' Enter` in one call gets coalesced; readline-style TUIs (coding agents, modern REPLs) treat it as a bracketed paste — the text appears but never submits.
- **`\n` is not Enter.** Use the key name `Enter` (or `C-m`). If a TUI swallows the named key, send a raw carriage return: `tmux -L claude-agent send-keys -t mytask -H 0d`.
- **Semicolons:** `;` is tmux's command separator. Keep payload text as one shell-quoted argument (as above) and it is safe.
- **Multi-line text:** don't type it line by line — use bracketed paste:

```bash
tmux -L claude-agent load-buffer -b blob /tmp/snippet.txt
tmux -L claude-agent paste-buffer -p -b blob -t mytask
```

### Named keys

| Key | Name | Key | Name |
|---|---|---|---|
| Enter | `Enter` | Ctrl+C | `C-c` |
| Escape | `Escape` | Ctrl+D | `C-d` |
| Tab | `Tab` | Ctrl+Z | `C-z` |
| Backspace | `BSpace` | Arrows | `Up` `Down` `Left` `Right` |
| Page up/down | `PPage` `NPage` | Home/End | `Home` `End` |
| Space (as key) | `Space` | Function | `F1`..`F12` |

## Reading output

First determine what kind of program you are looking at:

```bash
tmux -L claude-agent display-message -p -t mytask '#{alternate_on} #{pane_current_command}'
```

`alternate_on` is `1` for full-screen TUIs (vim, htop, coding-agent UIs) and `0` for line-based programs (shells, REPLs).

| Program type | Capture command |
|---|---|
| Full-screen TUI (`alternate_on` = 1) | `tmux -L claude-agent capture-pane -p -t mytask` (visible screen only — scrollback is meaningless) |
| REPL / line output | `tmux -L claude-agent capture-pane -p -J -t mytask -S -200` (last 200 history lines, wrapped lines rejoined) |
| Everything since start | `tmux -L claude-agent capture-pane -p -J -t mytask -S -` |
| Testing colors/attributes | add `-e` (includes ANSI escapes; omit otherwise — default capture is clean text) |

`-J` matters: long lines wrap in the pane, and a regex will not match across a wrap unless lines are rejoined.

For long sessions, capture the full scrollback to a file each time and diff against the previous capture to see only what is new.

Optional full transcript from the start (raw escapes included — sanitize before grepping):

```bash
tmux -L claude-agent pipe-pane -t mytask -o 'cat >> /tmp/mytask.transcript'
```

## Driving full-screen TUIs

TUIs read single keystrokes, not lines. Work in a reconnaissance-then-action loop:

1. Capture the visible screen.
2. Identify state: what is focused, what the menu shows, what the footer hints.
3. Send ONE action (`Down`, `Tab`, `Enter`, a single letter).
4. Capture again and verify the state changed as expected before the next action.

Useful extras:

```bash
tmux -L claude-agent resize-window -t mytask -x 120 -y 30   # test reflow/responsive layout
tmux -L claude-agent refresh-client -t mytask                # force redraw if output looks stale
```

## Testing coding-agent CLIs (Claude Code, Codex, etc.)

These are the hardest case: full-screen TUI + readline-style input box + streaming output. The recipe:

```bash
# 1. Session in a scratch project, generous size
env -u TMUX tmux -L claude-agent -f /dev/null new-session -d -s agenttest -c /tmp/scratch -x 200 -y 50
~/.claude/skills/tmux-interactive/scripts/wait-for-text.sh -t agenttest '([$%#>]|❯) *$'

# 2. Launch and wait for the UI to settle (not for a pattern — UI chrome varies)
tmux -L claude-agent send-keys -t agenttest -l -- 'claude'
tmux -L claude-agent send-keys -t agenttest Enter
~/.claude/skills/tmux-interactive/scripts/wait-for-idle.sh -t agenttest -s 2 -T 60

# 3. Send a prompt: text and Enter MUST be separate sends with a delay,
#    or the TUI treats it as a paste and never submits
tmux -L claude-agent send-keys -t agenttest -l -- 'What files are in this directory?'
sleep 0.3
tmux -L claude-agent send-keys -t agenttest Enter

# 4. Wait for the response: streaming pauses, so use a LONG stability window
~/.claude/skills/tmux-interactive/scripts/wait-for-idle.sh -t agenttest -s 5 -T 300
tmux -L claude-agent capture-pane -p -t agenttest

# 5. Exit cleanly, then kill
tmux -L claude-agent send-keys -t agenttest -l -- '/exit'
sleep 0.3
tmux -L claude-agent send-keys -t agenttest Enter
sleep 1
tmux -L claude-agent kill-session -t agenttest
```

Notes:

- If the agent under test asks a permission/confirmation question, treat it as a TUI: capture, read the options, send the single key it asks for.
- A too-short stability window (`-s 2`) fires during a thinking pause mid-response. If the captured screen ends mid-sentence or shows a spinner, wait again with a longer window.
- Verify the prompt actually submitted: capture right after step 3 — if the text is still sitting in the input box, the Enter was swallowed; resend `Enter` or use `send-keys -H 0d`.

## Pitfalls

1. **Shell-init race** — first `send-keys` eaten because `.zshrc`/`.bashrc` had not finished. Always `wait-for-text.sh` for the prompt after creating a session.
2. **Enter coalesced into a paste** — `'text' Enter` in one send never submits in readline-style TUIs. Separate sends, short delay between.
3. **Key-name interpretation** — payload without `-l` turns `Enter`/`Space`/`C-c` words into keystrokes.
4. **80x24 default** — unsized detached sessions break TUI layouts. Always `-x`/`-y`.
5. **Blank first capture** — capturing immediately after spawn shows nothing; wait for readiness.
6. **Pagers hijack the pane** — `less`, `git diff`, gdb paging block forever. Set `PAGER=cat GIT_PAGER=cat` in the session, or drive the pager as a TUI (`q` to quit).
7. **Editors you didn't want** — `git commit` opens an editor; pass `-m` or set `GIT_EDITOR=true` unless the editor is the thing under test.
8. **Wrong capture for the screen type** — scrollback (`-S -`) is meaningless for alternate-screen TUIs; visible-screen capture misses history for REPLs. Check `#{alternate_on}`.
9. **Wrapped lines break regexes** — use `-J`.
10. **Nested tmux refusal** — `$TMUX` set makes `new-session` fail; prefix with `env -u TMUX`.
11. **Crash destroys the pane** — launch programs from a shell inside the session (shell-first), not directly via `new-session`.
12. **Orphaned sessions** — name sessions per task, `kill-session` when done, sweep with `kill-server` on the private socket. List leftovers: `tmux -L claude-agent list-sessions`.
13. **Secrets in transcripts** — `pipe-pane` logs and captures include anything typed at password prompts. Don't log sessions that handle credentials.
14. **Escape-key delay** — tmux waits `escape-time` ms after Escape to disambiguate Alt-sequences. If Escape seems laggy in a TUI: `tmux -L claude-agent set -s escape-time 50`.

## References

- `references/recipes.md` — program-specific recipes: Python/Node REPLs, gdb/lldb, pagers, vim, ssh/password prompts, and a worked end-to-end coding-agent test.
