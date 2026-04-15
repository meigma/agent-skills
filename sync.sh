#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "usage: $0 <destination>" >&2
    exit 1
fi

dest="$1"
src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$dest"

rsync -av --delete \
    --exclude='.git/' \
    --exclude='.gitignore' \
    --exclude='LICENSE-*' \
    --exclude='README.md' \
    --exclude='justfile' \
    --exclude='sync.sh' \
    "$src"/ "$dest"/
