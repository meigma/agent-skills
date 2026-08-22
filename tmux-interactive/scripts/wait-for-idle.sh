#!/usr/bin/env bash
# Poll a tmux pane until its content stops changing for a stability window.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: wait-for-idle.sh -t TARGET [options]

Poll a tmux pane until its visible content stays unchanged for the
stability window. Use when you don't know what prompt or text to wait
for (TUI settling, streaming output finishing). A pane showing only
whitespace counts as still initializing, not idle.

Options:
  -t TARGET    tmux target pane, e.g. session or session:win.pane (required)
  -L SOCKET    tmux socket name (default: claude-agent)
  -T SECONDS   overall timeout, integer seconds (default: 60)
  -s SECONDS   stability window: how long content must stay unchanged
               to count as idle, integer seconds (default: 2)
  -i SECONDS   poll interval (default: 0.5)
  -h           show this help

Exit codes: 0 idle, 1 timed out, 2 usage error.
EOF
}

socket=claude-agent
timeout=60
stable=2
interval=0.5
target=""

while getopts ":t:L:T:s:i:h" opt; do
  case "$opt" in
    t) target=$OPTARG ;;
    L) socket=$OPTARG ;;
    T) timeout=$OPTARG ;;
    s) stable=$OPTARG ;;
    i) interval=$OPTARG ;;
    h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))

if [[ -z $target ]]; then
  usage >&2
  exit 2
fi

deadline=$(( $(date +%s) + timeout ))
last=""
stable_since=""
while :; do
  now=$(date +%s)
  content=$(tmux -L "$socket" capture-pane -p -t "$target" 2>/dev/null || true)
  trimmed=${content//[[:space:]]/}
  if [[ -n $trimmed && "$content" == "$last" ]]; then
    : "${stable_since:=$now}"
    if (( now - stable_since >= stable )); then
      exit 0
    fi
  else
    stable_since=""
    last=$content
  fi
  if (( now >= deadline )); then
    {
      echo "wait-for-idle: pane still changing (or blank) after ${timeout}s"
      echo "--- last capture (tail) ---"
      tail -n 40 <<<"$content"
    } >&2
    exit 1
  fi
  sleep "$interval"
done
