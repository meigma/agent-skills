#!/usr/bin/env bash
# Static triage of an untrusted download on media01.
#
# Builds the pinned scanner image on media01 (once per scanner change),
# refreshes the ClamAV database (at most every 12 hours), traces the path
# back to its qBittorrent torrent, scans it in a network-less, read-only,
# unprivileged container, and renders the verdict locally.
#
# usage: triage.sh [--profile media|software] <path on media01>
# exit:  0 PASS, 10 REVIEW, 20 BLOCK, anything else = triage failed
# env:   TRIAGE_TARGET (default nas01:media01), TRIAGE_OUT, VT_API_KEY
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
skill="$(dirname "$here")"
target="${TRIAGE_TARGET:-nas01:media01}"
profile=""
if [ "${1:-}" = "--profile" ]; then profile="$2"; shift 2; fi
if [ "$#" -ne 1 ]; then
    echo "usage: $0 [--profile media|software] <path on media01>" >&2
    exit 2
fi
path="${1%/}"
case "$path" in
    *,*) echo "paths containing commas are not supported" >&2; exit 2 ;;
    /data/*) ;;
    *) echo "path must be under /data on media01" >&2; exit 2 ;;
esac
if [ -z "$profile" ]; then
    case "$path" in
        /data/media/tv*|/data/media/movies*|/data/torrents/tv*|/data/torrents/movies*|/data/torrents/sonarr*|/data/torrents/radarr*|/data/usenet/complete/tv*|/data/usenet/complete/movies*) profile=media ;;
        *) profile=software ;;
    esac
fi
name="$(basename "$path")"
remote() { incus exec --project default "$target" -- "$@"; }

remote test -e "$path" || { echo "not found on $target: $path" >&2; exit 2; }

# Scanner image, tagged by the hash of its build inputs.
tag="$(cat "$skill/scanner/Dockerfile" "$skill/scanner/scan.py" | shasum -a 256 | cut -c1-12)"
if ! remote docker image inspect "untrusted-triage:$tag" >/dev/null 2>&1; then
    echo "building scanner image untrusted-triage:$tag on $target" >&2
    remote mkdir -p "/opt/untrusted-triage/$tag"
    for f in Dockerfile scan.py; do
        incus file push -q --project default "$skill/scanner/$f" "$target/opt/untrusted-triage/$tag/$f"
    done
    build_log="$(remote docker build -q -t "untrusted-triage:$tag" "/opt/untrusted-triage/$tag" 2>&1)" || { printf '%s\n' "$build_log" >&2; exit 1; }
    remote sh -c "docker images untrusted-triage --format '{{.Tag}}' | grep -vx '$tag' | sed 's/^/untrusted-triage:/' | xargs -r docker rmi -f >/dev/null; ls -d /opt/untrusted-triage/* | grep -v '/$tag\$' | xargs -r rm -rf"
fi

# ClamAV signatures: the only container step with network access.
remote docker volume create triage-clamdb >/dev/null
remote docker run --rm --user 0 -v triage-clamdb:/var/lib/clamav --entrypoint sh "untrusted-triage:$tag" -c \
    'chown -R clamav:clamav /var/lib/clamav
     if [ -z "$(find /var/lib/clamav -name "daily.c?d" -mmin -720)" ]; then freshclam --stdout --quiet 2>&1 | grep -v NotifyClamd || true; fi'

run_dir="${TRIAGE_OUT:-$HOME/.local/state/untrusted-file-triage}/$(date +%Y%m%d-%H%M%S)-$(printf '%s' "$name" | tr -cs 'A-Za-z0-9._-' '_' | cut -c1-60)"
mkdir -p "$run_dir"

# Provenance: the qBittorrent torrent whose files are this path's files.
# Sonarr/Radarr imports are hardlinks (same inode); an importer that copies
# leaves only identical names and sizes to match on.
remote python3 - "$path" > "$run_dir/provenance.json" <<'EOF'
import json, os, subprocess, sys
path = sys.argv[1]
def qbt(endpoint):
    out = subprocess.run(["docker", "exec", "qbittorrent", "curl", "-s", "http://127.0.0.1:8080/api/v2/" + endpoint],
                         capture_output=True, text=True).stdout
    return json.loads(out or "[]")
def walk(p, limit):
    if os.path.isfile(p):
        return [p]
    found = []
    for d, _, fs in os.walk(p):
        found += [os.path.join(d, f) for f in fs]
        if len(found) >= limit:
            break
    return found[:limit]
files = walk(path, 200)
inodes = {os.stat(f).st_ino for f in files}
sigs = {(os.path.basename(f), os.path.getsize(f)) for f in files if os.path.getsize(f) > 1024**2}
matches = []
for t in qbt("torrents/info"):
    cp = t.get("content_path") or ""
    if not cp.startswith("/data/") or not os.path.exists(cp):
        continue
    tfiles = walk(cp, 5000)
    if any(os.stat(f).st_ino in inodes for f in tfiles):
        how = "hardlinked files"
    elif sigs & {(os.path.basename(f), os.path.getsize(f)) for f in tfiles}:
        how = "same file names and sizes (copied, not hardlinked)"
    else:
        continue
    props = qbt("torrents/properties?hash=" + t["hash"])
    trackers = [x["url"] for x in qbt("torrents/trackers?hash=" + t["hash"]) if x["url"].startswith(("http", "udp"))]
    matches.append({"hash": t["hash"], "name": t["name"], "category": t.get("category"), "match": how,
                    "comment": props.get("comment"), "created_by": props.get("created_by"), "trackers": trackers})
json.dump({"torrents": matches}, sys.stdout)
EOF

echo "scanning $path (profile $profile)" >&2
remote sh -s -- "$path" "$profile" "$tag" "$name" > "$run_dir/scan.json" <<'EOF'
set -eu
path=$1 profile=$2 tag=$3 name=$4
out=$(mktemp -d /tmp/triage.XXXXXX)
trap 'rm -rf "$out"' EXIT
chown 65534:65534 "$out"
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
    --user 65534:65534 --memory 3g --memory-swap 3g --pids-limit 256 --cpus 4 \
    --tmpfs /tmp:rw,exec,size=1200m \
    -v triage-clamdb:/var/lib/clamav:ro \
    --mount "type=bind,source=$path,target=/sample,readonly" \
    -v "$out:/out" "untrusted-triage:$tag" --profile "$profile" --name "$name" >&2
cat "$out/scan.json"
EOF

set +e
python3 "$here/report.py" "$run_dir/scan.json" "$run_dir/provenance.json" | tee "$run_dir/report.md"
rc=${PIPESTATUS[0]}
set -e
echo "report: $run_dir/report.md" >&2
exit "$rc"
