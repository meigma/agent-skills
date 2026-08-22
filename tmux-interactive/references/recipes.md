# Program-specific recipes

All commands assume the conventions from SKILL.md: private socket `-L claude-agent`, session already created and at a shell prompt. `WAIT` below abbreviates `~/.claude/skills/tmux-interactive/scripts/wait-for-text.sh` and `IDLE` abbreviates `~/.claude/skills/tmux-interactive/scripts/wait-for-idle.sh` — type the full paths in real commands.

## Python REPL

Python 3.13+ ships a "fancy" REPL whose line editing interferes with send-keys. Force the basic one:

```bash
tmux -L claude-agent send-keys -t S -l -- 'PYTHON_BASIC_REPL=1 python3 -q'
tmux -L claude-agent send-keys -t S Enter
WAIT -t S '>>> *$'
tmux -L claude-agent send-keys -t S -l -- 'print(2 + 2)'
tmux -L claude-agent send-keys -t S Enter
WAIT -t S '>>> *$'          # prompt returns when the statement finished
tmux -L claude-agent capture-pane -p -J -t S -S -50
```

Multi-line blocks: paste via buffer (bracketed paste keeps indentation intact), then send Enter twice to close the block:

```bash
tmux -L claude-agent load-buffer -b py /tmp/block.py
tmux -L claude-agent paste-buffer -p -b py -t S
tmux -L claude-agent send-keys -t S Enter Enter
```

Exit: `send-keys -t S C-d` (or `exit()`).

## Node REPL

```bash
tmux -L claude-agent send-keys -t S -l -- 'node'
tmux -L claude-agent send-keys -t S Enter
WAIT -t S '^> *$'
```

Node's REPL echoes with ANSI rewrites; capture with `-J` and match on result text, not on exact line layout. Exit with `.exit` or two `C-c`.

## Debuggers (lldb, gdb)

Prefer lldb on macOS. Disable gdb pagination immediately or the first long output blocks the session:

```bash
tmux -L claude-agent send-keys -t S -l -- 'lldb ./mybinary'
tmux -L claude-agent send-keys -t S Enter
WAIT -t S '\(lldb\) *$'
# gdb instead: WAIT -t S '\(gdb\) *$' then send: set pagination off
```

Then one command per send, waiting for the `(lldb)` / `(gdb)` prompt between each. Breakpoint hits arrive asynchronously after `run`/`continue` — wait for the prompt pattern again, then capture to read the stop reason.

## Pagers and git

Disable pagers when output is what you want, before launching the program under test:

```bash
tmux -L claude-agent send-keys -t S -l -- 'export PAGER=cat GIT_PAGER=cat LESS=FRX'
tmux -L claude-agent send-keys -t S Enter
```

If a pager appears anyway: `Space` pages forward, `q` quits. For `git commit` without an editor, use `-m`; to test the editor flow itself, see vim below. For `git rebase -i`, set `GIT_SEQUENCE_EDITOR` to a script for deterministic edits, or drive vim by keys.

## vim / editors

vim is an alternate-screen TUI: capture the visible screen only, send single keys, verify mode from the status line after every action.

```bash
WAIT -t S -F 'mybranch'                      # wait for the file/UI to render
tmux -L claude-agent send-keys -t S -l -- 'iHello world'   # i enters insert mode, then text
tmux -L claude-agent send-keys -t S Escape
tmux -L claude-agent send-keys -t S -l -- ':wq'
tmux -L claude-agent send-keys -t S Enter
WAIT -t S '([$%#>]|❯) *$'                    # back at the shell
```

## ssh and password prompts

```bash
tmux -L claude-agent send-keys -t S -l -- 'ssh host'
tmux -L claude-agent send-keys -t S Enter
WAIT -t S -T 20 '[Pp]assword:'
```

Do NOT enable `pipe-pane` transcripts for sessions that handle credentials, and never echo a password into the conversation — ask the user to attach and type it themselves:

```
Please run: tmux -L claude-agent attach -t S
type the password, then detach with Ctrl+b d.
```

Then `WAIT` for the post-login prompt and continue.

## Worked example: end-to-end test of a coding-agent CLI

Scenario: verify that the `claude` CLI can answer a question about a scratch project. The same shape works for any agent TUI (codex, aider, etc.).

```bash
# Scratch project so the agent under test can't touch real code
mkdir -p /tmp/agent-scratch && cd /tmp/agent-scratch && git init -q && echo 'hello' > readme.txt

# 1. Session at a shell, generous size, wait for the prompt
env -u TMUX tmux -L claude-agent -f /dev/null new-session -d -s ctest -c /tmp/agent-scratch -x 200 -y 50
~/.claude/skills/tmux-interactive/scripts/wait-for-text.sh -t ctest '([$%#>]|❯) *$'
echo 'To watch: tmux -L claude-agent attach -t ctest  (detach: Ctrl+b d)'

# 2. Launch the agent CLI; wait for its UI to settle rather than for specific text
tmux -L claude-agent send-keys -t ctest -l -- 'claude'
tmux -L claude-agent send-keys -t ctest Enter
~/.claude/skills/tmux-interactive/scripts/wait-for-idle.sh -t ctest -s 2 -T 90

# 3. Snapshot the initial UI — confirm it launched (look for the input box / trust prompt).
tmux -L claude-agent capture-pane -p -t ctest
# If a trust/permission dialog is showing, read it and answer it as a TUI
# (usually Enter or a single number/letter key), then idle-wait again.

# 4. Send the test prompt: text, delay, Enter — three separate steps
tmux -L claude-agent send-keys -t ctest -l -- 'What does readme.txt contain? Answer in one line.'
sleep 0.3
tmux -L claude-agent send-keys -t ctest Enter

# 5. Confirm it submitted (input box should be empty / spinner visible)
sleep 1
tmux -L claude-agent capture-pane -p -t ctest

# 6. Wait for the full response: long stability window because LLM output streams with pauses
~/.claude/skills/tmux-interactive/scripts/wait-for-idle.sh -t ctest -s 5 -T 300
tmux -L claude-agent capture-pane -p -t ctest         # assert the answer mentions "hello"

# 7. Quit the agent, then the session
tmux -L claude-agent send-keys -t ctest -l -- '/exit'
sleep 0.3
tmux -L claude-agent send-keys -t ctest Enter
sleep 1
tmux -L claude-agent kill-session -t ctest
```

Failure triage at each step:

| Symptom | Likely cause | Fix |
|---|---|---|
| Step 3 capture is blank | UI not rendered yet | idle-wait longer; check the binary launched (`display-message -p -t ctest '#{pane_current_command}'`) |
| Step 5 shows your text still in the input box | Enter coalesced into a paste | resend `Enter`; if still stuck, `send-keys -t ctest -H 0d` |
| Step 6 times out | stability window shorter than thinking pauses | raise `-s`; check the screen for a permission question waiting for a key |
| Response truncated in capture | TUI scrolled within alternate screen | scroll up via `copy-mode` + `send-keys -t ctest PPage`, capture, `send-keys -t ctest q`; or re-ask with shorter expected output |
