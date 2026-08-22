#!/usr/bin/env bash
# Poll a tmux pane until its content matches a pattern or a timeout expires.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: wait-for-text.sh -t TARGET [options] PATTERN

Poll a tmux pane until its content matches PATTERN (extended regex by
default). Prints nothing on success. On timeout, dumps the tail of the
last capture to stderr so you can see what the pane actually showed.

Options:
  -t TARGET    tmux target pane, e.g. session or session:win.pane (required)
  -L SOCKET    tmux socket name (default: claude-agent)
  -T SECONDS   timeout, integer seconds (default: 30)
  -i SECONDS   poll interval (default: 0.5)
  -S LINES     history lines included in each capture (default: 200)
  -F           treat PATTERN as a fixed string, not a regex
  -h           show this help

Exit codes: 0 matched, 1 timed out, 2 usage error.
EOF
}

socket=claude-agent
timeout=30
interval=0.5
lines=200
fixed=0
target=""

while getopts ":t:L:T:i:S:Fh" opt; do
  case "$opt" in
    t) target=$OPTARG ;;
    L) socket=$OPTARG ;;
    T) timeout=$OPTARG ;;
    i) interval=$OPTARG ;;
    S) lines=$OPTARG ;;
    F) fixed=1 ;;
    h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))

pattern=${1:-}
if [[ -z $target || -z $pattern ]]; then
  usage >&2
  exit 2
fi

deadline=$(( $(date +%s) + timeout ))
content=""
while :; do
  content=$(tmux -L "$socket" capture-pane -p -J -t "$target" -S "-$lines" 2>/dev/null || true)
  if [[ $fixed -eq 1 ]]; then
    grep -qF -- "$pattern" <<<"$content" && exit 0
  else
    grep -qE -- "$pattern" <<<"$content" && exit 0
  fi
  if (( $(date +%s) >= deadline )); then
    {
      echo "wait-for-text: timed out after ${timeout}s waiting for: $pattern"
      echo "--- last capture (tail) ---"
      tail -n 40 <<<"$content"
    } >&2
    exit 1
  fi
  sleep "$interval"
done
